import { db, serializeTaskForRunTask } from './models'
import { isNotNullish, isNullish } from './null-utils'
import { Task, TaskStatus, removeDuplicatesByKey } from './models'
import { TaskHelper } from './task-helper'
import { ScraperType } from './scraper-type'
import { TaskResults } from './task-results'
import { isDontCache } from 'botasaurus/dontcache'
import { formatExc } from 'botasaurus/utils'
import { cleanDataInPlace } from 'botasaurus/output'
import { getScraperErrorMessage, Server } from './server'
import { isLargeFile, isNotEmptyObject } from './utils'

/**
 * Task priority levels for queue ordering
 */
export enum TaskPriority {
    DEFAULT_PRIORITY = 0,
    URGENT_PRIORITY = 1
}
export function extractParentIds(tasks: any[]) {
    const parentIdsSet = new Set<any>();
    tasks.forEach((task) => {
        if (task.parent_task_id) {
            parentIdsSet.add(task.parent_task_id);
        }
    });
    return Array.from(parentIdsSet);
}

async function queryPendingTasks(maxTasks: number | null, query: any) {
    if (isNotNullish(maxTasks)) {
        // @ts-ignore
        return db.findAsync(query).sort({ priority: -1, sort_id: -1 }).limit(maxTasks) as unknown as Task[]

    } else {
        return await db.findAsync(query).sort({ priority: -1, sort_id: -1 }) as unknown as Task[]

    }
}


export async function getPendingTasks(query: any, maxTasks: number | null) {
    const tasks = await queryPendingTasks(maxTasks, query)
    
            if (tasks.length === 0) {
                return [];
            }

            const validScraperNames = Server.getScrapersNames()
            const validScraperNamesSet = new Set(validScraperNames)

            for (const task of tasks) {
                if (!validScraperNamesSet.has(task.scraper_name)) {
                    const validNamesString = validScraperNames.join(', ')
                    throw new Error(getScraperErrorMessage(validScraperNames, task.scraper_name, validNamesString))
                }
            }            

            const taskIds = tasks.map(t => t.id);
            const parentIds = extractParentIds(tasks)

            // Mark tasks as IN_PROGRESS
            await db.updateAsync(
                { id: { $in: taskIds } },
                {
                    $set: {
                        status: TaskStatus.IN_PROGRESS,
                        started_at: new Date()
                    }
                },
                { multi: true }
            );



            // Update parent tasks if applicable
            if (parentIds.length > 0) {
                try {
                    await db.updateAsync(
                        { id: { $in: parentIds }, started_at: null },
                        { $set: { status: TaskStatus.IN_PROGRESS, started_at: new Date() } },
                        { multi: true }
                    );
                } catch (parentErr) {
                    console.error('Error updating parent tasks:', parentErr);
                }
            }

            // Serialize tasks for workers
            return tasks.map(task => serializeTaskForRunTask(task));
}

class TaskExecutor {
    currentCapacity: { browser?: number; request?: number; task?: number } | Record<string, number> = {
        browser: 0,
        request: 0,
        task: 0,
    }

    public load() {
        if (Server.isScraperBasedRateLimit) {
            this.currentCapacity = {}
        } else {
            this.currentCapacity = { browser: 0, request: 0, task: 0 }
        }

        Server.validateRateLimit()
    }

    public async start(): Promise<void> {
        await this.fixInProgressTasks()
        await this.completePendingButCompletedAllTask()
        this.startTaskWorker()
    }

    protected startTaskWorker(): void {
        if (Server.isScraperBasedRateLimit) {
            setImmediate(this.taskWorkerScraperBased.bind(this))
        } else {
            setImmediate(this.taskWorkerScraperTypeBased.bind(this))
        }
    }

    private async completePendingButCompletedAllTask(): Promise<void> {
        try {
            const pendingTasks = await new Promise<Task[]>((resolve, reject) => {
                db.find(
                  {
                    $and: [
                      { is_all_task: true },
                      { status: TaskStatus.PENDING },
                    ],
                  },
                  (err: any, tasks: Task[]) => {
                    if (err) {
                      reject(err)
                    } else {
                      resolve(tasks)
                    }
                  }
                )
              })
          
              for (const parentTask of pendingTasks) {
                const parentId = parentTask.id
                const isAllChildTasksDone = await TaskHelper.areAllChildTaskDone(parentId)
                if (isAllChildTasksDone) {
                  const is_large: any = parentTask.is_large
      
                  const failedChildrenCount = await TaskHelper.getFailedChildrenCount(parentId)
                  const status = failedChildrenCount ? TaskStatus.FAILED : TaskStatus.COMPLETED
                  
                  const removeDuplicatesBy = Server.getRemoveDuplicatesBy(parentTask.scraper_name)
                  // Find the oldest started_at task that is the parent of the current task
                  const oldestParentTask = await this.findOldestChildTask(parentId)
                  
                  const extra_updates = (finished_at: any) => ({
                      started_at: oldestParentTask ? oldestParentTask.started_at : finished_at,
                  })
                  
                  await TaskHelper.readCleanSaveTask(
                      parentId,
                      removeDuplicatesBy,
                      status,
                      is_large, 
                      extra_updates
                  )
                }
              }
        } catch (error) {
            console.error(error)
        }
    }
    
    private async findOldestChildTask(parentId: number) {
        return await new Promise<Task | null>((resolve, reject) => {
            db.find({
                $and: [
                    { parent_task_id: parentId },
                    { started_at: { $exists: true } },
                ],
            })
            .sort({ started_at: 1 }) // oldest
            .limit(1)
            .exec((err: any, tasks: any[]) => {
                if (err) {
                    reject(err)
                } else {
                    resolve(tasks.length > 0 ? tasks[0] : null)
                }
            })
        })
    }

    private async fixInProgressTasks(): Promise<void> {
        try {
            // Reset all IN_PROGRESS tasks back to PENDING on startup
            await new Promise<void>((resolve, reject) => {
                db.update(
                    { status: TaskStatus.IN_PROGRESS },
                    { $set: { status: TaskStatus.PENDING, started_at: null, finished_at: null, } },
                    { multi: true },
                    (err) => {
                        if (err) {
                            reject(err)
                        } else {
                            resolve()
                        }
                    }
                )
            })
        } catch (error) {
            console.error(error)
        }
    }
    protected async taskWorkerScraperBased(): Promise<void> {
        await this.processScraperBasedTasks();
        setTimeout(this.taskWorkerScraperBased.bind(this), 1000);
    }

    protected async taskWorkerScraperTypeBased(): Promise<void> {
        await this.processScraperTypeBasedTasks();
        setTimeout(this.taskWorkerScraperTypeBased.bind(this), 1000);
    }

    private async processScraperTypeBasedTasks(): Promise<void> {
        const browserScrapers = Server.getBrowserScrapers().length > 0
        const requestScrapers = Server.getRequestScrapers().length > 0
        const taskScrapers = Server.getTaskScrapers().length > 0

        if (browserScrapers) {
            await this.processTasksByType(ScraperType.BROWSER)
        }

        if (requestScrapers) {
            await this.processTasksByType(ScraperType.REQUEST)
        }

        if (taskScrapers) {
            await this.processTasksByType(ScraperType.TASK)
        }
    }

    private async processScraperBasedTasks(): Promise<void> {
        const scrapers = Server.getScrapersNames()
        for (const scraperName of scrapers) {
            await this.processTasksByScraper(scraperName)
        }
    }

    private async processTasksByType(scraperType: string): Promise<void> {
        const [hasCapacity, currentCount, rateLimit]  = this.getCapacityInfo(scraperType)
        if (hasCapacity) {
            await this.executePendingTasks(
                this.buildScraperTypeQuery(scraperType),
                currentCount,
                rateLimit,
                scraperType
            )
        }
    }
    protected buildScraperTypeQuery(scraperType: string): any {
        return {
            $and: [
                { status: TaskStatus.PENDING },
                { scraper_type: scraperType },
                { is_all_task: false },
            ],
        }
    }

    getCapacityInfo(key: string): [boolean, number, number|null] {
        const rateLimit: number | null = this.getMaxRunningCount(key);
        const currentCount: number = this.getCurrentRunningCount(key);
        const hasCapacity: boolean = isNullish(rateLimit) || currentCount < rateLimit;
        return [hasCapacity, currentCount, rateLimit];
    }
    public hasCapacity(key: string): boolean {
        return this.getCapacityInfo(key)[0];
    }
    private async processTasksByScraper(scraperName: string): Promise<void> {
        const [hasCapacity, currentCount, rateLimit]  = this.getCapacityInfo(scraperName)
        if (hasCapacity) {
            await this.executePendingTasks(
                this.buildScraperNameQuery(scraperName),
                currentCount,
                rateLimit,
                scraperName
            )
        }
    }

    protected buildScraperNameQuery(scraperName: string): any {
        return {
            $and: [
                { status: TaskStatus.PENDING },
                { scraper_name: scraperName },
                { is_all_task: false },
            ],
        }
    }

    private getMaxRunningCount(key: string): number {
        // @ts-ignore
        return Server.getRateLimit()[key]
    }

    private getCurrentRunningCount(key: string): number {
        // @ts-ignore
        return this.currentCapacity[key] ?? 0

    }

    private async executePendingTasks(
        taskFilter: any,
        current: number,
        limit: number|null,
        key: string
    ): Promise<void> {
        // @ts-ignore
        const tasks = await getPendingTasks(taskFilter, isNotNullish(limit) ?  limit - current  :null)
        
        for (const task of tasks) {
            this.runTaskAndUpdateCapacity(key, task)
        }
    }

    protected runTaskAndUpdateCapacity(
        key: string,
        taskJson: any
    ): void {
        setImmediate(this.runTask.bind(this), taskJson)
        this.incrementCapacity(key)
    }
     incrementCapacity(key: string): void {
        // @ts-ignore
        this.currentCapacity[key] = (this.currentCapacity[key] ?? 0) + 1;
    }
    
     decrementCapacity(key: string): void {
        // @ts-ignore
        this.currentCapacity[key] = (this.currentCapacity[key] ?? 0) - 1;
    }
    
    protected async runTask(task: any): Promise<void> {
        const key = Server.isScraperBasedRateLimit ? task.scraper_name : task.scraper_type
        const taskId = task.id
        const scraperName = task.scraper_name
        const parent_task_id = task.parent_task_id
        const metadata = isNotEmptyObject(task.metadata) ? { metadata: task.metadata } : {}
        const taskData = task.data

        const fn = Server.getScrapingFunction(scraperName)
        let exceptionLog: any = null
        try {
            let result: any = null
            try {
                result = await fn(taskData, {
                    ...metadata,
                    parallel: null,
                    cache: false,
                    beep: false,
                    raiseException: true,
                    closeOnCrash: true,
                    output: null,
                    createErrorLogs: false,
                    returnDontCacheAsIs: true,
                })
                let isResultDontCached = false
                if (isDontCache(result)) {
                    isResultDontCached = true
                    result = result.data
                }

                result = cleanDataInPlace(result)
                const removeDuplicatesBy = Server.getRemoveDuplicatesBy(scraperName)
                if (removeDuplicatesBy) {
                    result = removeDuplicatesByKey(result, removeDuplicatesBy)
                }

                this.decrementCapacity(key)
                await this.reportTaskSuccess(taskId, result, isResultDontCached, scraperName, taskData, parent_task_id, key)
                
            } catch (error) {
                this.decrementCapacity(key)
                exceptionLog = formatExc(error)
                console.error(error)
                await this.reportTaskFailure(taskId, exceptionLog, parent_task_id, key)
            } 
        } catch (error) {
            console.error("Error in run_task", error)
        }
    }

    protected async reportTaskFailure(taskId: any, exceptionLog: any, parent_task_id: any, _key: string) {
        await this.markTaskAsFailure(taskId, exceptionLog)
        if (parent_task_id) {
            await this.updateParentTask(taskId, exceptionLog)
        }
    }

    protected async reportTaskSuccess(taskId: any, result: any, isResultDontCached: boolean, scraperName: any, taskData: any, parent_task_id: any, _key: string) {
        await this.markTaskAsSuccess(
            taskId,
            result,
            isResultDontCached ? false : Server.cache,
            scraperName,
            taskData
        )
        if (parent_task_id) {
            await this.updateParentTask(taskId, result)
        }
    }

    protected async updateParentTask(taskId: number, result: any[]) {
        const task = await new Promise<Task>((resolve, reject) => {
            db.findOne({ id: taskId }, (err, task: Task) => {
                if (err) {
                    reject(err)
                } else {
                    resolve(task)
                }
            })
        })
        // ensures task is not deleted
        if (task) {
            const parentId = task.parent_task_id
            const scraperName = task.scraper_name
    
            if (parentId) {
                const removeDuplicatesBy = Server.getRemoveDuplicatesBy(scraperName)
                await this.completeParentTaskIfPossible(
                    parentId,
                    removeDuplicatesBy,
                    result,
                )
            }        
        }
    }

    async completeParentTaskIfPossible(
        parentId: number,
        removeDuplicatesBy: string | null,
        result: any[]
    ) {
        const parentTask = await TaskHelper.getTask(
            parentId,
            [TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        )

        if (parentTask) {
            const is_large: any = parentTask.is_large
            await TaskHelper.updateParentTaskResults(parentId, result, is_large)
            const isAllChildTasksDone = await TaskHelper.areAllChildTaskDone(
                parentId
            )
            if (isAllChildTasksDone) {
                const failedChildrenCount = await TaskHelper.getFailedChildrenCount(
                    parentId
                )
                const status = failedChildrenCount
                    ? TaskStatus.FAILED
                    : TaskStatus.COMPLETED
                await TaskHelper.readCleanSaveTask(
                    parentId,
                    removeDuplicatesBy,
                    status,
                    is_large
                )
            }
        }
    }
    async completeAsMuchAllTaskAsPossible(
        parentId: number,
        removeDuplicatesBy: string | null
    ): Promise<void> {
        const isAllChildTasksDone = await TaskHelper.areAllChildTaskDone(parentId)
        if (isAllChildTasksDone) {
            const failedChildrenCount = await TaskHelper.getFailedChildrenCount(
                parentId
            )
            const status = failedChildrenCount
                ? TaskStatus.FAILED
                : TaskStatus.COMPLETED
            await TaskHelper.collectAndSaveAllTask(
                parentId,
                null,
                removeDuplicatesBy,
                status, 
                false,
            )
        } else {
            await TaskHelper.collectAndSaveAllTask(
                parentId,
                null,
                removeDuplicatesBy,
                TaskStatus.IN_PROGRESS,
                false,
            )
        }
    }

    protected async markTaskAsFailure(
        taskId: number,
        exceptionLog: string
    ): Promise<void> {
        await TaskResults.saveTask(taskId, [exceptionLog])
        const updateResult = await TaskHelper.updateTask(
            taskId,
            {
                status: TaskStatus.FAILED,
                finished_at: new Date(),
            },
            [TaskStatus.IN_PROGRESS],
        )
        if (!updateResult) {
            TaskResults.deleteTask(taskId)
        }
    }

    protected async markTaskAsSuccess(
        taskId: number,
        result: any[],
        cacheTask: boolean,
        scraperName: string,
        data: any
    ): Promise<void> {
        const taskPath = await TaskResults.saveTask(taskId, result)
        const isLarge = isLargeFile(taskPath)
        
        if (cacheTask) {
             await TaskResults.saveCachedTask(scraperName, data, result, isLarge)
        }
        const updateResult = await TaskHelper.updateTask(taskId, {
            result_count: result.length,
            status: TaskStatus.COMPLETED,
            finished_at: new Date(),
            is_large: isLarge
        }, [TaskStatus.IN_PROGRESS] )
        if (!updateResult) {
            TaskResults.deleteTask(taskId)
        }
    }
}

export { TaskExecutor }
