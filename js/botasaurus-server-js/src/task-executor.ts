import { db, serializeTaskForRunTask } from './models'
import { isNotNullish, isNullish } from './null-utils'
import { Task, TaskStatus, removeDuplicatesByKey } from './models'
import { TaskHelper, PushDataWriter } from './task-helper'
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

    protected readonly ABORT_CHECK_INTERVAL: number = 1000
    
    // Centralized abortion checking state
    private toCheckAbortTasks: Set<number> = new Set()
    private abortedTasksState: Record<number, boolean> = {}
    private abortCheckIntervalId: ReturnType<typeof setInterval> | null = null

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
    
    /**
     * Adds a task to the abortion check set and starts the shared interval if not running.
     */
    private addToAbortCheck(taskId: number): void {
        this.toCheckAbortTasks.add(taskId)
        this.abortedTasksState[taskId] = false
        
        // Start the shared interval if not already running
        if (!this.abortCheckIntervalId) {
            this.abortCheckIntervalId = setInterval(
                () => this.checkAllTasksAbortion(),
                this.ABORT_CHECK_INTERVAL
            )
        }
    }

    /**
     * Removes a task from the abortion check set and cleans up if no more tasks.
     */
    private removeFromAbortCheck(taskId: number): void {
        this.toCheckAbortTasks.delete(taskId)
        delete this.abortedTasksState[taskId]
        
        // Stop the interval if no more tasks to check
        if (this.toCheckAbortTasks.size === 0 && this.abortCheckIntervalId) {
            clearInterval(this.abortCheckIntervalId)
            this.abortCheckIntervalId = null
        }
    }

    /**
     * Checks abortion status for all tasks in the set.
     * Called by the shared interval.
     */
    private async checkAllTasksAbortion(): Promise<void> {
        if (this.toCheckAbortTasks.size === 0) {
            // No tasks to check, stop the interval
            if (this.abortCheckIntervalId) {
                clearInterval(this.abortCheckIntervalId)
                this.abortCheckIntervalId = null
            }
            return
        }

        try {
            const taskIds = Array.from(this.toCheckAbortTasks)
            const results = await this.getTasksAbortionResults(taskIds)
            
            let allAborted = true
            for (const taskIdStr of Object.keys(results)) {
                const taskId = Number(taskIdStr)
                const isAborted = results[taskId]
                this.abortedTasksState[taskId] = isAborted
                if (isAborted) {
                    // Remove aborted tasks from the check set
                    this.toCheckAbortTasks.delete(taskId)
                } else {
                    allAborted = false
                }
            }
            
            // Stop interval if all tasks are aborted or set is empty
            if (allAborted || this.toCheckAbortTasks.size === 0) {
                if (this.abortCheckIntervalId) {
                    clearInterval(this.abortCheckIntervalId)
                    this.abortCheckIntervalId = null
                }
            }
        } catch (error) {
            console.error('Error checking tasks abortion status:', error)
        }
    }

    /**
     * Batch fetches abortion results for multiple task IDs.
     * Returns an object of taskId -> isAborted.
     */
    async getTasksAbortionResults(taskIds: number[]): Promise<Record<number, boolean>> {
        if (taskIds.length === 0) {
            return {}
        }
        const results: Record<number, boolean> = {}

        // Batch query for all tasks
        const tasks = await db.findAsync(
            { id: { $in: taskIds } },
            { id: 1, status: 1 }
        ) as unknown as Array<{ id: number, status: string }>
        
        const taskIdToTaskMap: Record<number, { id: number, status: string }> = {}
        for (const task of tasks) {
            taskIdToTaskMap[task.id] = task
        }
        
        // Check each task
        for (const taskId of taskIds) {
            if (!taskIdToTaskMap[taskId]) {
                // Task was deleted - treat as aborted
                results[taskId] = true
            } else {
                const task = taskIdToTaskMap[taskId]
                // We do not check for ABORTED status here as even it is failed, failed then restart, we want task to exit
                results[taskId] = task?.status !== TaskStatus.IN_PROGRESS
            }
        }
        
        return results
    }

    /**
     * Creates an isAborted function for a task.
     * Uses centralized abortion checking for efficiency.
     */
    protected createIsAborted(taskId: number): { isAborted: () => boolean, cleanup: () => void } {
        let isFirstCall = true

        const isAborted = () => {
            if (isFirstCall) {
                isFirstCall = false
                // Add to centralized abortion checking
                this.addToAbortCheck(taskId)
            }
            return this.abortedTasksState[taskId] ?? false
        }

        const cleanup = () => {
            this.removeFromAbortCheck(taskId)
        }

        return { isAborted, cleanup }
    }

    protected async runTask(task: any): Promise<void> {
        const key = Server.isScraperBasedRateLimit ? task.scraper_name : task.scraper_type
        const taskId = task.id
        const scraperName = task.scraper_name
        const parent_task_id = task.parent_task_id
        const metadata = isNotEmptyObject(task.metadata) ? { metadata: task.metadata } : {}
        const taskData = task.data

        const fn = Server.getScrapingFunction(scraperName)
        const { isAborted, cleanup } = this.createIsAborted(taskId)
        const removeDuplicatesBy = Server.getRemoveDuplicatesBy(scraperName)
        
        // Create PushDataWriter for pushData functionality
        const onResultCountUpdate = this.createResultCountUpdater(taskId)
        const pushDataWriter = new PushDataWriter(taskId, removeDuplicatesBy, onResultCountUpdate)
        const pushData = pushDataWriter.push.bind(pushDataWriter)

        let exceptionLog: any = null
        try {
            let result: any = null
            try {
                result = await fn(taskData, {
                    ...metadata,
                    isAborted,
                    pushData,
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


                this.decrementCapacity(key)
                cleanup()

                if (pushDataWriter.wasUsed()) {
                    // Push any returned result as well
                    await pushData(result)
                    
                    // Close stream and perform normalization (returns final result count)
                    await pushDataWriter.close()
                    
                    // pushData was used - report success with the normalized result
                    await this.reportTaskSuccessWithPushData(
                        taskId,
                        pushDataWriter.getFilePath(),
                        pushDataWriter.getItemCount(),
                        isResultDontCached,
                        scraperName,
                        taskData,
                        parent_task_id,
                        key
                    )
                } else {
                    // Normal flow - result was returned
                    result = cleanDataInPlace(result)
                    if (removeDuplicatesBy && Array.isArray(result)) {
                        result = removeDuplicatesByKey(result, removeDuplicatesBy)
                    }
                    await this.reportTaskSuccess(taskId, result, isResultDontCached, scraperName, taskData, parent_task_id, key)
                }
                
            } catch (error) {
                await pushDataWriter.close()
                cleanup()
                this.decrementCapacity(key)
                exceptionLog = formatExc(error)
                console.error(error)
                await this.reportTaskFailure(taskId, exceptionLog, parent_task_id, key)
            } 
        } catch (error) {
            await pushDataWriter.close()
            cleanup()
            console.error("Error in run_task", error)
        }
    }

    protected async reportTaskSuccessWithPushData(
        taskId: number,
        taskFilePath:string,
        itemCount: number,
        isResultDontCached: boolean,
        scraperName: string,
        taskData: any,
        parent_task_id: number | null,
        _key: string
    ) {
        await this.markTaskAsSuccessWithFile(
            taskId,
            taskFilePath,
            itemCount,
            isResultDontCached ? false : Server.cache,
            scraperName,
            taskData
        )
        if (parent_task_id) {
            await this.updateParentTaskStreaming(taskId)
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
        const task = await db.findOneAsync({ id: taskId }) as unknown as Task | null
        if (task && task.parent_task_id) {
            const removeDuplicatesBy = Server.getRemoveDuplicatesBy(task.scraper_name)
            await this.completeParentTaskIfPossible(
                task.parent_task_id,
                removeDuplicatesBy,
                result,
            )
        }
    }

    /**
     * Updates parent task by streaming child results (without loading into memory).
     */
    protected async updateParentTaskStreaming(taskId: number) {
        const task = await db.findOneAsync({ id: taskId }) as unknown as Task | null
        if (task && task.parent_task_id) {
            const removeDuplicatesBy = Server.getRemoveDuplicatesBy(task.scraper_name)
            await this.completeParentTaskIfPossibleStreaming(
                taskId,
                task.parent_task_id,
                removeDuplicatesBy,
            )
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
            await this.finalizeParentIfAllChildrenDone(parentId, removeDuplicatesBy, is_large)
        }
    }

    /**
     * Streams child task results to parent and completes parent if all children done.
     */
    async completeParentTaskIfPossibleStreaming(
        childId: number,
        parentId: number,
        removeDuplicatesBy: string | null,
    ) {
        const parentTask = await TaskHelper.getTask(
            parentId,
            [TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
        )

        if (parentTask) {
            const is_large: any = parentTask.is_large
            await TaskHelper.streamChildToParentResults(childId, parentId, is_large)
            await this.finalizeParentIfAllChildrenDone(parentId, removeDuplicatesBy, is_large)
        }
    }

    /**
     * Checks if all children are done and finalizes the parent task.
     */
    private async finalizeParentIfAllChildrenDone(
        parentId: number,
        removeDuplicatesBy: string | null,
        is_large: boolean
    ) {
        const isAllChildTasksDone = await TaskHelper.areAllChildTaskDone(parentId)
        if (isAllChildTasksDone) {
            const failedChildrenCount = await TaskHelper.getFailedChildrenCount(parentId)
            const status = failedChildrenCount ? TaskStatus.FAILED : TaskStatus.COMPLETED
            await TaskHelper.readCleanSaveTask(
                parentId,
                removeDuplicatesBy,
                status,
                is_large
            )
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
        await this.updateTaskAsCompleted(taskId, result.length, isLarge)
    }

    /**
     * Marks a task as success when the result file already exists (pushData case).
     */
    protected async markTaskAsSuccessWithFile(
        taskId: number,
        taskFilePath: string,
        itemCount: number,
        cacheTask: boolean,
        scraperName: string,
        data: any
    ): Promise<void> {
        const isLarge = isLargeFile(taskFilePath)
        
        if (cacheTask) {
            await TaskResults.copyTaskToCachedTask(scraperName, data, itemCount, taskFilePath, isLarge)
        }
        await this.updateTaskAsCompleted(taskId, itemCount, isLarge)
    }

    /**
     * Common method to update task status as completed.
     */
    protected async updateTaskAsCompleted(
        taskId: number,
        resultCount: number,
        isLarge: boolean
    ): Promise<void> {
        const updateResult = await TaskHelper.updateTask(taskId, {
            result_count: resultCount,
            status: TaskStatus.COMPLETED,
            finished_at: new Date(),
            is_large: isLarge
        }, [TaskStatus.IN_PROGRESS])
        if (!updateResult) {
            TaskResults.deleteTask(taskId)
        }
    }

    /**
     * Creates a callback to update task result count during pushData.
     * Override in subclasses to customize or disable updates.
     */
    protected createResultCountUpdater(taskId: number): ((result_count: number) => Promise<any>) | undefined {
        return (result_count: number) => TaskHelper.updateTask(taskId, { result_count })
    }
}

export { TaskExecutor }
