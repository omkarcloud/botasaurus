import { Mutex } from 'async-mutex';
import { TaskExecutor } from './task-executor';
import { Server } from './server';
import { ScraperType } from './scraper-type';
import { isNotNullish } from './null-utils'

/**
 * Backoff configuration for polling
 */
const BACKOFF_CONFIG = {
    baseInterval: 1000,      // 1 second
    maxInterval: 30000,      // 30 seconds
    backoffFactor: 2
};

/**
 * Retry configuration for HTTP requests
 */
const RETRY_CONFIG = {
    maxRetries: 6,
    initialDelay: 1000,      // 1 second
    backoffFactor: 2,
    maxDelay: 60000          // 60 seconds
};

/**
 * Add random jitter to delay (0-10% of current delay)
 */
function addJitter(delay: number): number {
    return delay + Math.random() * 0.1 * delay;
}

/**
 * Sleep helper
 */
function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function sleepWithJitter(delay: number) {
    await sleep(addJitter(delay))
}

/**
 * Calculate backoff interval based on consecutive empty polls
 */
function calculateBackoffInterval(baseInterval: number, backoffFactor: number, maxInterval: number, consecutiveEmptyPolls: number): number {
    return Math.min(
        baseInterval * Math.pow(backoffFactor, consecutiveEmptyPolls),
        maxInterval
    );
}

/**
 * WorkerExecutor handles task execution in Kubernetes worker mode.
 * It polls the master for tasks and reports results back.
 */
export class WorkerExecutor extends TaskExecutor {
    private masterUrl: string;
    private inProgressTaskIds: Set<number> = new Set();
    public isShuttingDown: boolean = false;
    private masterMutex = new Mutex();
    private consecutiveEmptyPolls: number = 0;

    constructor(masterUrl: string) {
        super();
        this.masterUrl = masterUrl;
        this.setupGracefulShutdown();
    }

    /**
     * Override: Worker does NOT use local task processing.
     * It polls the master for tasks instead.
     */
    protected override startTaskWorker(): void {
        if (Server.isScraperBasedRateLimit) {
            this.startScraperNameBasedWorker();
        } else {
            this.startScraperTypeBasedWorker();
        }
    }

    /**
     * Worker loop for scraper-type-based rate limiting.
     * Polls master for tasks by scraper type.
     */
    private async startScraperTypeBasedWorker(): Promise<void> {
        const keys: string[] = [];
        
        if (Server.getBrowserScrapers().length > 0) {
            keys.push(ScraperType.BROWSER);
        }
        if (Server.getRequestScrapers().length > 0) {
            keys.push(ScraperType.REQUEST);
        }
        if (Server.getTaskScrapers().length > 0) {
            keys.push(ScraperType.TASK);
        }
        
        this.runWorkerLoop(keys);
    }

    /**
     * Worker loop for scraper-name-based rate limiting.
     * Polls master for tasks by scraper name.
     */
    private async startScraperNameBasedWorker(): Promise<void> {
        this.runWorkerLoop(Server.getScrapersNames());
    }

    /**
     * Single worker loop that polls for tasks by keys sequentially.
     */
    private async runWorkerLoop(keys: string[]): Promise<void> {
        while (!this.isShuttingDown) {
            let foundTasks = false;
            
            for (const key of keys) {
                if (this.isShuttingDown) break;
                
                try {
                    const tasks = await this.pollForTasks(key);
                    
                    if (tasks && tasks.length > 0) {
                        foundTasks = true;
                        await this.runNextTasks(tasks, key);
                    }
                } catch (error) {
                    console.error(`[Worker] Error polling for ${key} tasks:`, error);
                }
            }
            
            if (!foundTasks) {
                this.consecutiveEmptyPolls++;
            }

            await sleepWithJitter(calculateBackoffInterval(BACKOFF_CONFIG.baseInterval, BACKOFF_CONFIG.backoffFactor, BACKOFF_CONFIG.maxInterval, this.consecutiveEmptyPolls));
        }
    }

    /**
     * Calculate available capacity for a given key.
     * Returns null for unlimited, a positive number for available capacity,
     * or NO_CAPACITY constant if no capacity available.
     */
    private getAvailableCapacity(key: string): number | null | false {
        const [hasCapacity, currentCount, rateLimit] = this.getCapacityInfo(key);
        
        if (!hasCapacity) {
            return false; // No capacity
        }

        // null rateLimit means unlimited
        if (!isNotNullish(rateLimit)) {
            return null; // Unlimited
        }

        const availableCapacity = rateLimit! - currentCount;
        if (availableCapacity <= 0) {
            return false; // No capacity
        }
        return availableCapacity;
    }

    /**
     * Poll master for tasks. Checks capacity and makes appropriate API call.
     * Uses mutex to ensure only one concurrent request to master at a time.
     */
    private async pollForTasks(key: string): Promise<any[]> {
        return this.masterMutex.runExclusive(async () => {
            try {
                const maxTasks = this.getAvailableCapacity(key);
                
                // No capacity available
                if (maxTasks === false) {
                    return [];
                }
                
                // maxTasks: null = unlimited, number = limited
                // @ts-ignore
                const maxTasksParam = isNotNullish(maxTasks) ? `&max_tasks=${encodeURIComponent(maxTasks!.toString())}` : '';
                const endpoint = Server.isScraperBasedRateLimit
                    ? `/k8s/acquire-tasks-by-name?scraper_name=${encodeURIComponent(key)}${maxTasksParam}`
                    : `/k8s/acquire-tasks-by-type?scraper_type=${encodeURIComponent(key)}${maxTasksParam}`;
                
                const response = await this.getFromMaster(endpoint);
                return response?.tasks || [];
            } catch (error) {
                console.error(`[Worker] Failed to poll for tasks (${key}):`, error);
                return [];
            }
        });
    }

    /**
     * Report task success to master and fetch next tasks.
     * Uses mutex to ensure only one concurrent request to master at a time.
     */
    protected override async reportTaskSuccess(
        taskId: number,
        result: any,
        isResultDontCached: boolean,
        scraperName: string,
        taskData: any,
        parentTaskId: number | null,
        key: string,
    ): Promise<void> {
        this.inProgressTaskIds.delete(taskId);
        await this.masterMutex.runExclusive(async () => {
            try {
                const capacity = this.buildCapacityInfo(key);

                const requestPayload = {
                    taskId,
                    result,
                    isDontCache: isResultDontCached,
                    scraperName,
                    taskData,
                    capacity, 
                    parentTaskId
                };

                const response = await this.postToMaster('/k8s/task-completed', requestPayload, true);
                await this.runNextTasks(response?.nextTasks, key);
            } catch (error) {
                console.error('[Worker] Failed to report success to master:', error);
            }
        });
    }

    /**
     * 
     * Report task failure to master and fetch next tasks.
     * Uses mutex to ensure only one concurrent request to master at a time.
     */
    protected override async reportTaskFailure(
        taskId: number,
        error: string,
        parentTaskId: number | null,
        key: string,

    ) {
        this.inProgressTaskIds.delete(taskId);
        await this.masterMutex.runExclusive(async () => {
            try {
                const capacity = this.buildCapacityInfo(key);

                const requestPayload = {
                    taskId,
                    error,
                    capacity,
                    parentTaskId
                };

                const response = await this.postToMaster('/k8s/task-failed', requestPayload, true);
                await this.runNextTasks(response?.nextTasks, key);
            } catch (error) {
                console.error('[Worker] Failed to report failure to master:', error);
            }
        });
    }

    /**
     * Build capacity info for piggyback pattern.
     * Returns null if shutting down or no capacity available.
     */
    private buildCapacityInfo(key: string): { scraperType?: string; scraperName?: string; maxTasks?: number } | null {
        if (this.isShuttingDown) {
            return null;
        }

        const availableCapacity = this.getAvailableCapacity(key);
        
        // No capacity available
        if (availableCapacity === false) {
            return null;
        }

        // availableCapacity: null = unlimited (omit maxTasks), number = limited
        if (Server.isScraperBasedRateLimit) {
            // @ts-ignore
            return isNotNullish(availableCapacity) ? { scraperName: key, maxTasks: availableCapacity }
                : { scraperName: key };
        } else {
            // @ts-ignore
            return isNotNullish(availableCapacity) ? { scraperType: key, maxTasks: availableCapacity }
                : { scraperType: key };
        }
    }



    private runNextTasks(nextTasks: any, key: string) {
        
        if (!nextTasks || nextTasks.length === 0) {
            return;
        }

        if (this.isShuttingDown) {
            console.log(`[Worker] Shutting down, skipping next tasks`);
            return this.releaseTasksToPending(nextTasks.map((task:any) => task.id));
            
        }
        this.consecutiveEmptyPolls = 0
        for (const task of nextTasks) {
            this.inProgressTaskIds.add(task.id);
            this.runTaskAndUpdateCapacity(key, task)
        }
        return;
    }

    /**
     * HTTP GET from master with retry logic.
     */
    private async getFromMaster(endpoint: string): Promise<any> {
        return await this.postToMaster(endpoint, null, false, "GET");
    }

    /**
     * HTTP POST to master with retry logic.
     */
    private async postToMaster(endpoint: string, payload: any, persistent = false, method = "POST", ): Promise<any> {
        const url = `${this.masterUrl}${endpoint}`;
        let retries = 0;
        let delay = RETRY_CONFIG.initialDelay;

        while (retries <= RETRY_CONFIG.maxRetries || persistent) {
            try {
                let response 
                if (method === "POST") {
                    response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                } else if (method === "GET") {
                    response = await fetch(url, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                }
                else {
                    throw new Error(`Invalid method: ${method}`);
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error: any) {
                retries++;

                if (retries > RETRY_CONFIG.maxRetries && !persistent) {
                    throw error;
                }

                console.warn(`[Worker] Request to ${endpoint} failed (attempt ${retries}/${RETRY_CONFIG.maxRetries}): ${error.message}. Retrying in ${delay}ms...`);
                
                delay = calculateBackoffInterval(RETRY_CONFIG.initialDelay, RETRY_CONFIG.backoffFactor, RETRY_CONFIG.maxDelay, retries);
                await sleepWithJitter(delay)
                
            }
        }
    }

    /**
     * Set up graceful shutdown handlers.
     * On SIGTERM/SIGINT, notify master about in-progress tasks.
     */
    private setupGracefulShutdown(): void {
        const shutdownHandler = async (signal: string) => {
            if (this.isShuttingDown) return;
            
            console.log(`[Worker] Received ${signal}, initiating graceful shutdown...`);
            this.isShuttingDown = true;

            // Immediately notify master about in-progress tasks
            if (this.inProgressTaskIds.size > 0) {
                try {
                    const inProgressTaskIds = Array.from(this.inProgressTaskIds)
                    await this.releaseTasksToPending(inProgressTaskIds);
                } catch (error) {
                    console.warn('[Worker] Failed to notify master of shutdown, tasks will recover via visibility timeout:', error);
                }
            }
        };

        process.on('SIGTERM', () => shutdownHandler('SIGTERM'));
        process.on('SIGINT', () => shutdownHandler('SIGINT'));
        
        // Handle uncaught exceptions - try to release tasks
        process.on('uncaughtException', async (error) => {
            console.error('[Worker] Uncaught exception:', error);
            await shutdownHandler('uncaughtException');
        });
    }

    private async releaseTasksToPending(inProgressTaskIds: number[]) {
        const response =  await this.postToMaster('/k8s/worker-shutdown', {
            inProgressTaskIds
        })
        console.log(`[Worker] Released ${response?.releasedCount || 0} tasks back to queue`);
    }
}
