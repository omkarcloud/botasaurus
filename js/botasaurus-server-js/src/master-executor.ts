import { Mutex } from 'async-mutex';
import { getPendingTasks, TaskExecutor, TaskPriority } from './task-executor';
import { db, Task, TaskStatus } from './models';
import { Server } from './server';
import { TaskResults } from './task-results';
export const DEFAULT_TASK_TIMEOUT = 8 * 60 * 60
/**
 * Payload for task completion from worker
 */
export interface TaskCompletionPayload {
    taskId: number;
    result: any;
    isDontCache: boolean;
    scraperName: string;
    parentTaskId?: number | null;
    taskData: any;
    capacity?: {
        scraperType?: string;
        scraperName?: string;
        maxTasks: number;
    } | null;
}

/**
 * Payload for task failure from worker
 */
export interface TaskFailurePayload {
    taskId: number;
    error: string;
    parentTaskId?: number | null;
    capacity?: {
        scraperType?: string;
        scraperName?: string;
        maxTasks: number;
    } | null;
}

/**
 * Payload for pushData chunk from worker
 */
export interface PushDataChunkPayload {
    taskId: number;
    chunk: any[];
}

/**
 * Payload for pushData completion from worker
 */
export interface PushDataCompletePayload {
    taskId: number;
    itemCount: number;
    isDontCache: boolean;
    scraperName: string;
    taskData: any;
    parentTaskId?: number | null;
    capacity?: {
        scraperType?: string;
        scraperName?: string;
        maxTasks: number;
    } | null;
}


/**
 * Stale task recovery interval: 60 seconds
 */
const STALE_TASK_RECOVERY_INTERVAL = 60 * 1000;

/**
 * MasterExecutor handles task distribution in Kubernetes master mode.
 * It does NOT execute tasks locally - workers request tasks via API.
 * The master reclaims stale tasks (visibility timeout expired) and
 * manages task state across the distributed system.
 */
export class MasterExecutor extends TaskExecutor {
    private taskTimeout: number | Record<string, number>;
    private acquireMutex = new Mutex();

    constructor(taskTimeout: number | Record<string, number>) {
        super();
        this.taskTimeout = taskTimeout;
    }

    /**
     * Override: Master does NOT execute tasks locally.
     * Instead, it starts the stale task recovery loop.
     */
    protected override startTaskWorker(): void {
        this.startStaleTaskRecoveryLoop();
    }

    

    /**
     * Periodically scan for tasks stuck IN_PROGRESS beyond visibility timeout.
     * Reset them to PENDING with URGENT_PRIORITY for re-acquisition.
     */
    // TODO: check
    private startStaleTaskRecoveryLoop(): void {
        const recoverStaleTasks = async () => {
            try {
                const now = new Date();
                const nowTime = now.getTime();
                const taskTimeout = this.taskTimeout;
                const isScraperBasedRateLimit = Server.isScraperBasedRateLimit;

                // Use $where to filter stale tasks directly in the query
                const staleTasks = await db.findAsync({
                    status: TaskStatus.IN_PROGRESS,
                    is_all_task: false,
                    $where: function(this: Task) {
                        if (!this.started_at) return false;
                        
                        let timeoutSeconds: number;
                        
                        if (typeof taskTimeout === 'number') {
                            timeoutSeconds = taskTimeout;
                        } else if (isScraperBasedRateLimit) {
                            timeoutSeconds = taskTimeout[this.scraper_name];
                        } else {
                            timeoutSeconds = taskTimeout[this.scraper_type];
                        }
                        timeoutSeconds= timeoutSeconds ?? DEFAULT_TASK_TIMEOUT
                        
                        const timeoutMs = timeoutSeconds * 1000;
                        const startedAtTime = this.started_at.getTime();
                        const elapsedMs = nowTime - startedAtTime;
                        
                        return elapsedMs > timeoutMs;
                    }
                }) as Task[];

                if (staleTasks.length > 0) {
                    const taskIds = staleTasks.map(t => t.id);
                    await this.resetTasksToPending(taskIds);
                }
            } catch (error) {
                console.error('[Master] Error in stale task recovery:', error);
            }

            // Schedule next recovery check
            setTimeout(recoverStaleTasks, STALE_TASK_RECOVERY_INTERVAL);
        };

        // Start the recovery loop
        setTimeout(recoverStaleTasks, STALE_TASK_RECOVERY_INTERVAL);
    }

    /**
     * Reset tasks back to PENDING status with URGENT priority.
     * Only resets if tasks are currently IN_PROGRESS or PENDING (idempotent).
     */
    async resetTasksToPending(taskIds: number[]): Promise<number> {
        if (taskIds.length === 0) return 0;
        
        const result = await db.updateAsync(
            { 
                id: { $in: taskIds }, 
                status: { $in: [TaskStatus.IN_PROGRESS, TaskStatus.PENDING] }
            },
            {
                $set: {
                    status: TaskStatus.PENDING,
                    started_at: null,
                    finished_at: null,
                    priority: TaskPriority.URGENT_PRIORITY,
                }
            },
            { multi: true }
        );
        
        return result.numAffected;
    }

    /**
     * Atomically acquire up to N pending tasks of a specific scraper type.
     * Uses mutex locking to prevent race conditions.
     */
    async acquireTasksByScraperType(scraperType: string, maxTasks: number|null): Promise<any[]> {
        return this.acquireTasksWithMutex(
            this.buildScraperTypeQuery(scraperType),
            maxTasks
        );
    }

    /**
     * Atomically acquire up to N pending tasks of a specific scraper name.
     * Uses mutex locking to prevent race conditions.
     */
    async acquireTasksByScraperName(scraperName: string, maxTasks: number|null): Promise<any[]> {
        return this.acquireTasksWithMutex(
            this.buildScraperNameQuery(scraperName),
            maxTasks
        );
    }

    /**
     * Internal method to acquire tasks with mutex protection.
     */
    private async acquireTasksWithMutex(query: any, maxTasks: number|null): Promise<any[]> {
        return this.acquireMutex.runExclusive(() => getPendingTasks(query, maxTasks));
    }

    /**
     * Handle task completion from worker.
     * Piggyback pattern: also return new tasks for worker's available capacity.
     */
    async handleTaskCompletion(payload: TaskCompletionPayload): Promise<{ nextTasks: any[] }> {
        const { taskId, result, isDontCache, scraperName, taskData, capacity, parentTaskId } = payload;

        try {
            // 1. Process and save the result
            await this.reportTaskSuccess(taskId, result, isDontCache, scraperName, taskData, parentTaskId, null as any)
        } catch (error) {
            console.error('[Master] Error handling task completion:', error);
        }

        // 4. Piggyback: Acquire next tasks if capacity is provided
        return this.acquireNextTasks(capacity)
    }

    private async acquireNextTasks(capacity: { scraperType?: string; scraperName?: string; maxTasks: number|null } | null | undefined) {
        let nextTasks: any[] = []
        if (capacity) {
            if (capacity.scraperType) {
                nextTasks = await this.acquireTasksByScraperType(capacity.scraperType, capacity.maxTasks)
            } else if (capacity.scraperName) {
                nextTasks = await this.acquireTasksByScraperName(capacity.scraperName, capacity.maxTasks)
            }
        }
        return { nextTasks };
    }

    /**
     * Handle task failure from worker.
     * Piggyback pattern: also return new tasks for worker's available capacity.
     */
    async handleTaskFailure(payload: TaskFailurePayload): Promise<{ nextTasks: any[] }> {
        const { taskId, error, capacity, parentTaskId } = payload;

        try {
            await this.reportTaskFailure(taskId, error, parentTaskId, null as any)
        } catch (err) {
            console.error('[Master] Error handling task failure:', err);
        }

        // 4. Piggyback: Acquire next tasks if capacity is provided
        return this.acquireNextTasks(capacity)
    }

    /**
     * Handle worker graceful shutdown.
     * Immediately release tasks back to pending status with urgent priority.
     */
    async handleWorkerShutdown(inProgressTaskIds: number[]): Promise<{ releasedCount: number }> {
        if (inProgressTaskIds.length === 0) return { releasedCount: 0 };
        
        const releasedCount = await this.resetTasksToPending(inProgressTaskIds);
        console.log(`[Master] Released ${releasedCount}/${inProgressTaskIds.length} tasks from shutting down worker`);
        return { releasedCount };
    }

    /**
     * Handle pushData chunk from worker.
     * Appends chunk to the task's result file.
     */
    async handlePushDataChunk(payload: PushDataChunkPayload) {
        const { taskId, chunk } = payload;

        try {
            if (chunk && chunk.length > 0) {
                await TaskResults.appendAllTask(taskId, chunk);
            }
            return {};
        } catch (error) {
            console.error('[Master] Error handling pushData chunk:', error);
            throw error;
        }
    }

    /**
     * Handle pushData completion from worker.
     * Finalizes the task (caching, status update, parent update).
     * Piggyback pattern: also return new tasks for worker's available capacity.
     */
    async handlePushDataComplete(payload: PushDataCompletePayload): Promise<{ nextTasks: any[] }> {
        const { taskId, itemCount, isDontCache, scraperName, taskData, parentTaskId, capacity } = payload;
        const taskFilePath = TaskResults.generateTaskFilePath(taskId);

        try {
            await this.reportTaskSuccessWithPushData(taskId, taskFilePath, itemCount, isDontCache, scraperName, taskData, parentTaskId as any, null as any)
        } catch (error) {
            console.error('[Master] Error handling pushData complete:', error);
        }

        // Piggyback: Acquire next tasks if capacity is provided
        return this.acquireNextTasks(capacity);
    }
}
