import * as fs from 'fs';
import { isNotNullish, isNullish } from "./null-utils";
import { createTask, db, Task } from "./models";
import { TaskResults } from "./task-results";
import { TaskStatus } from "./models";
import { NDJSONWriteStream } from "./ndjson"
import { _has } from 'botasaurus/cache'
import { isLargeFile } from './utils'
import { sleep } from 'botasaurus/utils'
import { normalizeData, normalizeItem } from 'botasaurus/output'

export function createProjection(ets: string[]) {
    return ets.reduce((acc: any, field) => {
        acc[field] = 1;
        return acc;
    }, {});
}


function populateMissingKeys(newKeys: string[], allKeysMapping: any) {
    let wasPopulated = false
    for (const key of newKeys) {
        if (!(key in allKeysMapping)) {
            allKeysMapping[key] = null
            wasPopulated = true 
        }
    }
    return wasPopulated
}

function createKeyToNullMapping(newLocal: any): any {
    return Object.keys(newLocal).reduce((acc: any, key: string) => {
        acc[key] = null
        return acc
    }, {})
}
function deleteFile(filePath:string) {
    return new Promise((resolve, _) => {
        fs.unlink(filePath, (_) => {
                resolve(null);
        });
    });
}
  
async function moveFile(tempFilePath:string, taskFilePath:string) {
    try {
        await new Promise((resolve, reject) => {
            fs.rename(tempFilePath, taskFilePath, (err) => {
                if (err) {
                    // this occurs in windows, don't know why. 
                    return reject(err) // Reject the promise on error
                }
                resolve(null)
            })
        })
    } catch (error) {
        console.error("MOVE FILE FAILED", error)
        // no need now. 
        // TODO: REMOVE ERRORS ASAP. ONCE WE NO LONGER SEE THAT IN PROGRESS CONTINOUS BUG, noote there is no performance loss here.
        console.error("DELETE FAILED, RETRYING...")
        
        try {
            await deleteFile(taskFilePath)        
        } catch (error) {
            console.error("DELETE FAILED, RETRYING 2...")
            await sleep(1)    
            await deleteFile(taskFilePath)        
        }
        
        console.error("DELETE taskFilePathTemp")
        
        try {
            await renameTemporaryFile(tempFilePath, taskFilePath)    
        } catch (error) {
            await sleep(1)
            console.error("DELETE taskFilePathTemp 2")
            await renameTemporaryFile(tempFilePath, taskFilePath)
            
        }
    }
}

function renameTemporaryFile(tempFilePath: string, taskFilePathTemp: string) {
    return new Promise((resolve, reject) => {
        fs.rename(tempFilePath, taskFilePathTemp, (err) => {
            if (err) {
                // this occurs in windows, don't know why. 
                return reject(err) // Reject the promise on error
            }
            resolve(null)
        })
    })
}

export interface KeyCollectionResult {
    allKeysMapping: any
    firstItemKeyCount: number
    didEarlyExit: boolean
}

function isErrorItem(item: any) {
    return typeof item === 'string'
}

export async function collectAllKeysFromIds(ids: number[], allowEarlyExit: boolean): Promise<KeyCollectionResult> {
    let allKeysMapping: any = null
    let firstItemKeyCount = 0
    let lastKeysChangedIndex: null | number = null
    let didEarlyExit = false
    let timesNewKeysAdded = 0
    
    let index = 0
    // @ts-ignore
    await TaskResults.streamMultipleTask(ids, (item, ix) => {


        if (isErrorItem(item)) {
            // these are errors
            return
          }
          
        index++

        
        const itemKeys = Object.keys(item)
        if (allKeysMapping === null) {
            // First item: initialize with its keys
            allKeysMapping = createKeyToNullMapping(item)
            firstItemKeyCount = itemKeys.length
        } else {
            const wasPopulated = populateMissingKeys(itemKeys, allKeysMapping)
            if (wasPopulated) {
                lastKeysChangedIndex = index
                timesNewKeysAdded++
            }
        }
        if (allowEarlyExit) {
            // After 10000 items, if keys changed <= 2 times, no normalization needed - exit early
            if (index >= 10000 && timesNewKeysAdded <= 2) {
                didEarlyExit = true
                return false
            }

            // 50000 items since changed.
            if (lastKeysChangedIndex !== null && index - lastKeysChangedIndex > 50000) {
                didEarlyExit = true
                return false
            }
        }
    })

    return { allKeysMapping, firstItemKeyCount, didEarlyExit }
}


function shouldNormalize(allKeys: string[] | null, firstItemKeyCount: number) {
    return allKeys && allKeys.length !== firstItemKeyCount
}

/**
 * Write deduplicated tasks  and normalize if needed tasks to a file.
 * @param ids - The ids of the tasks to write.
 * @param taskFilePath - The path to the task file.
 * @param allKeysMapping - The mapping of all keys.
 * @param firstItemKeyCount - The count of the first item's keys.
 * @param didEarlyExit - Whether to exit early.
 * @param removeDuplicatesBy - The key to remove duplicates by.
 */
async function writeDeduplicatedTasks(
    ids: number[],
    taskFilePath: string,
    allKeysMapping: any,
    firstItemKeyCount: number,
    didEarlyExit: boolean,
    removeDuplicatesBy: string | null
): Promise<number> {
    let itemsCount = 0
    const allKeys = allKeysMapping ? Object.keys(allKeysMapping) : null
    const shouldNormalizeFlag = shouldNormalize(allKeys, firstItemKeyCount)
    let needsRerun = false

    const tempfile = taskFilePath + '.temp'
    const ndjsonWriteStream = new NDJSONWriteStream(tempfile)
    const seen = new Set()

    try {
        // @ts-ignore
        await TaskResults.streamMultipleTask(ids, async (item) => {
            if (isErrorItem(item)) {
                // these are errors
                return
              }
              
            // If we did early exit, check if this item has new keys
            if (didEarlyExit) {
                const itemKeys = Object.keys(item)
                for (const key of itemKeys) {
                    if (!(key in allKeysMapping)) {
                        // Found a new key - need to rerun key collection fully
                        needsRerun = true
                        return false
                    }
                }
            }

            if (shouldNormalizeFlag) {
                item = normalizeItem(allKeys!, item)
            }

            if (removeDuplicatesBy) {
                if (removeDuplicatesBy in item && !isNullish(item[removeDuplicatesBy])) {
                    if (!seen.has(item[removeDuplicatesBy])) {
                        seen.add(item[removeDuplicatesBy])
                        await ndjsonWriteStream.push(item)
                        itemsCount++
                    }
                } else {
                    await ndjsonWriteStream.push(item)
                    itemsCount++
                }
            } else {
                await ndjsonWriteStream.push(item)
                itemsCount++
            }
        })

        await ndjsonWriteStream.end()

        if (needsRerun) {
            // Rerun key collection fully (no early exit)
            const fullResult = await collectAllKeysFromIds(ids, false)
            // Recursively call write with the complete keys and didEarlyExit=false
            return writeDeduplicatedTasks(
                ids,
                taskFilePath,
                fullResult.allKeysMapping,
                fullResult.firstItemKeyCount,
                false,
                removeDuplicatesBy
            )
        }

        await moveFile(tempfile, taskFilePath)
    } catch (error) {
        console.error('Error occurred while processing tasks:', error)
        await ndjsonWriteStream.end()
        throw error
    }

    return itemsCount
}

export class PushDataWriter {
    private stream: NDJSONWriteStream | null = null
    // @ts-ignore
    private taskFilePath: string
    private removeDuplicatesBy: string | null
    private seen: Set<any> = new Set()
    private itemCount = 0
    private lastReportedCount = 0
    private taskId: number
    private isPushDataUsed = false
    private onResultCountUpdate?: ((count: number) => Promise<void>)
    
    // Key collection for normalization
    private allKeysMapping: Record<string, null> | null = null
    private firstItemKeyCount = 0

    constructor(
        taskId: number,
        removeDuplicatesBy: string | null,
        onResultCountUpdate?: (count: number) => Promise<any>
    ) {
        this.taskId = taskId
        this.removeDuplicatesBy = removeDuplicatesBy
        this.onResultCountUpdate = onResultCountUpdate
    }

    async push(data: Record<string, any> | Record<string, any>[]): Promise<void> {
        this.isPushDataUsed = true
        if (!this.stream) {
            this.taskFilePath = TaskResults.generateTaskFilePath(this.taskId)
            this.stream = new NDJSONWriteStream(this.taskFilePath)
        }

        const items = normalizeData(data)

        for (const item of items) {
            // Handle deduplication if removeDuplicatesBy is set
            if (this.removeDuplicatesBy && this.removeDuplicatesBy in item && !isNullish(item[this.removeDuplicatesBy])) {
                const key = item[this.removeDuplicatesBy]
                if (this.seen.has(key)) continue
                this.seen.add(key)
            }
            
            // Collect keys for normalization
            const itemKeys = Object.keys(item)
            if (this.allKeysMapping === null) {
                // First item: initialize with its keys
                this.allKeysMapping = createKeyToNullMapping(item)
                this.firstItemKeyCount = itemKeys.length
            } else {
                // Add any new keys
                populateMissingKeys(itemKeys, this.allKeysMapping)
            }
            
            await this.stream.push(item)
            this.itemCount++
        }

        // Report count update after each push call
        await this.reportCountUpdate()
    }

    private async reportCountUpdate(): Promise<void> {
        if (!this.onResultCountUpdate) return
        
        const isFirstUpdate = this.lastReportedCount === 0
        const difference = this.itemCount - this.lastReportedCount
        
        if (isFirstUpdate || difference >= 10) {
            await this.onResultCountUpdate(this.itemCount)
            this.lastReportedCount = this.itemCount
        }
    }

    async close() {
        if (this.stream) {
            await this.stream.end()
            this.stream = null
            
            const allKeys = this.allKeysMapping ? Object.keys(this.allKeysMapping) : null
            const shouldNormalizeFlag = shouldNormalize(allKeys, this.firstItemKeyCount)
        
            if (shouldNormalizeFlag) {
                // Perform normalization pass with writeDeduplicatedTasks
                // Pass removeDuplicatesBy as null since deduplication already happened during push
                this.itemCount = await writeDeduplicatedTasks(
                    [this.taskId],
                    this.taskFilePath,
                    this.allKeysMapping,
                    this.firstItemKeyCount,
                    false, // didEarlyExit - we collected all keys
                    null   // removeDuplicatesBy - already deduplicated during push
                )
            }
            // Update final count
            await this.onResultCountUpdate?.(this.itemCount)
        }
    }

    wasUsed(): boolean {
        return this.isPushDataUsed
    }

    getItemCount(): number {
        return this.itemCount
    }

    getFilePath(): string {
        return this.taskFilePath
    }

    getRemoveDuplicatesBy(): string | null {
        return this.removeDuplicatesBy
    }
}

async function normalizeAndDeduplicateChildrenTasks(ids: number[], parentId: number, removeDuplicatesBy: string | null) {
    const taskFilePath = TaskResults.generateTaskFilePath(parentId)

    // First pass: collect all unique keys from all objects (with early exit allowed)
    const { allKeysMapping, firstItemKeyCount, didEarlyExit } = await collectAllKeysFromIds(ids, true)

    // Second pass: write deduplicated tasks (will rerun key collection if needed)
    const itemsCount = await writeDeduplicatedTasks(
        ids,
        taskFilePath,
        allKeysMapping,
        firstItemKeyCount,
        didEarlyExit,
        removeDuplicatesBy
    )

    return [itemsCount, taskFilePath]
}


class TaskHelper {
    static async getCompletedChildrenIds(
        parentId: number,
        exceptTaskId?: any,
    ): Promise<any[]> {
        const query: any = {
            parent_task_id: parentId,
            status: TaskStatus.COMPLETED,
            result_count: { $gte: 1 },
        };

        if (exceptTaskId) {
            query.id = { $ne: exceptTaskId };
        }

        const docs = await db.findAsync(query, { id: 1 }).sort({ sort_id: -1 }) as any[];
        return docs.map((doc) => doc.id);
    }

    static async getChildrenIdsWithResults(parentId: number): Promise<any[]> {
        const query = {
            parent_task_id: parentId,
            result_count: { $gte: 1 },
            status: { $in: [TaskStatus.COMPLETED] }, // status in success
        };

        const docs = await db.findAsync(query, { id: 1 }).sort({ sort_id: -1 }) as any[];
        const results = docs.map((doc) => doc.id);

        return results;
    }
    

    static async areAllChildTaskDone(parentId: number): Promise<boolean> {
        const doneChildrenCount = await TaskHelper.getDoneChildrenCount(
            parentId
        );
        const childCount = await TaskHelper.getAllChildrenCount(parentId);

        return doneChildrenCount === childCount;
    }

    static getAllChildrenCount(
        parentId: number,
        exceptTaskId?: number
    ): Promise<number> {
        return new Promise((resolve, reject) => {
            const query: any = { parent_task_id: parentId };
            if (exceptTaskId) {
                query.id = { $ne: exceptTaskId };
            }

            db.count(query, (err: Error | null, count: number) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(count);
                }
            });
        });
    }

    static getDoneChildrenCount(
        parentId: number,
        exceptTaskId?: number
    ): Promise<number> {
        return new Promise((resolve, reject) => {
            const query: any = {
                parent_task_id: parentId,
                status: {
                    $in: [
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.ABORTED,
                    ],
                },
            };
            if (exceptTaskId) {
                query.id = { $ne: exceptTaskId };
            }

            db.count(query, (err: Error | null, count: number) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(count);
                }
            });
        });
    }

    static isTaskCompletedOrFailed(taskId: number): Promise<boolean> {
        return new Promise((resolve, reject) => {
            db.findOne(
                {
                    id: taskId,
                    status: { $in: [TaskStatus.COMPLETED, TaskStatus.FAILED] },
                },
                (err: Error | null, task: any) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(isNotNullish(task));
                    }
                }
            );
        });
    }

    static getPendingOrExecutingChildCount(
        parentId: number,
        exceptTaskId?: number
    ): Promise<number> {
        return new Promise((resolve, reject) => {
            const query: any = {
                parent_task_id: parentId,
                status: { $in: [TaskStatus.PENDING, TaskStatus.IN_PROGRESS] },
            };
            if (exceptTaskId) {
                query.id = { $ne: exceptTaskId };
            }

            db.count(query, (err: Error | null, count: number) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(count);
                }
            });
        });
    }

    static getFailedChildrenCount(
        parentId: number,
        exceptTaskId?: number
    ): Promise<number> {
        return new Promise((resolve, reject) => {
            const query: any = {
                parent_task_id: parentId,
                status: TaskStatus.FAILED,
            };
            if (exceptTaskId) {
                query.id = { $ne: exceptTaskId };
            }

            db.count(query, (err: Error | null, count: number) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(count);
                }
            });
        });
    }

    static getAbortedChildrenCount(
        parentId: number,
        exceptTaskId?: number
    ): Promise<number> {
        return new Promise((resolve, reject) => {
            const query: any = {
                parent_task_id: parentId,
                status: TaskStatus.ABORTED,
            };
            if (exceptTaskId) {
                query.id = { $ne: exceptTaskId };
            }

            db.count(query, (err: Error | null, count: number) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(count);
                }
            });
        });
    }

    static deleteTask(taskId: number, isAllTask: boolean): Promise<void> {
        return new Promise((resolve, reject) => {
            db.remove({ id: taskId }, {}, (err: Error | null) => {
                if (err) {
                    reject(err);
                } else {
                    if (isAllTask) {
                        resolve(TaskResults.deleteAllTask(taskId));
                    } else {
                        resolve(TaskResults.deleteTask(taskId));
                    }
                }
            });
        });
    }

    static deleteChildTasks(taskId: number): Promise<void> {
        return new Promise((resolve, reject) => {
            db.find(
                { parent_task_id: taskId },
                (err: Error | null, tasks: any[]) => {
                    if (err) {
                        return reject(err);
                    }

                    const ids = tasks.map((task) => task.id);
                    db.remove(
                        { parent_task_id: taskId },
                        { multi: true },
                        (removeErr: Error | null) => {
                            if (removeErr) {
                                return reject(removeErr);
                            } else {
                                return resolve(TaskResults.deleteTasks(ids));
                            }
                        }
                    );
                }
            );
        });
    }

    static updateTask(
        taskId: number,
        data: any,
        inStatus?: string[]
    ): Promise<number> {
        const query: any = { id: taskId };
        if (inStatus) {
            query.status = { $in: inStatus };
        }

        return TaskHelper.updateTaskByQuery(query, data);
    }

    static updateTaskByQuery(query: any, data: any): Promise<number> {
        return new Promise((resolve, reject) => {
            db.update(
                query,
                { $set: data },
                {},
                (err: Error | null, numReplaced: number) => {
                    if (err) {
                        reject(err)
                    } else {
                        resolve(numReplaced)
                    }
                }
            )
        })
    }

    static abortTask(taskId: number): Promise<number> {
        const now = new Date();
        const abortableStatuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS];
        return new Promise((resolve, reject) => {
            db.update(
                { id: taskId, status: { $in: abortableStatuses }, finished_at: null },
                { $set: { finished_at: now } },
                {},
                (err: any, _: any) => {
                    if (err) {
                        reject(err);
                    } else {
                        this.updateTask(taskId, { status: TaskStatus.ABORTED }, abortableStatuses)
                            .then(resolve)
                            .catch(reject);
                    }
                }
            );
        });
    }

    static async retryTask(taskId: number){
        return db.updateAsync(
                { id: taskId },
            { $set: { status: TaskStatus.PENDING, started_at: null, finished_at: null, result_count: 0 } },
            {},
        );
    }

    static async retryFailedChildTasks(parentId: number){
        return db.updateAsync(
                { parent_task_id: parentId, status: TaskStatus.FAILED },
                { $set: { status: TaskStatus.PENDING, started_at: null, finished_at: null, result_count: 0 } },
                { multi: true },
            );
    }

    static async retryParentTask(parentId: number){
        await db.updateAsync(
            { id: parentId },
            { $set: {  finished_at: null } },
            {},
        )
        await db.updateAsync(
            { id: parentId, status: TaskStatus.FAILED },
            { $set: { status: TaskStatus.PENDING} },
            {},
        )
    }

    static async abortChildTasks(taskId: number) {
        const now = new Date();
        const abortableStatuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS];
        await new Promise((resolve, reject) => {
            db.update(
                { parent_task_id: taskId, status: { $in: abortableStatuses }, finished_at: null },
                { $set: { finished_at: now } },
                { multi: true },
                (err: Error | null, numReplaced: number) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(numReplaced);
                    }
                }
            );
        });
        await new Promise((resolve, reject) => {
            db.update(
                { parent_task_id: taskId, status: { $in: abortableStatuses } },
                { $set: { status: TaskStatus.ABORTED } },
                { multi: true },
                (err: Error | null, numReplaced: number) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(numReplaced);
                    }
                }
            );
        });
    }

    static async collectAndSaveAllTask(
        parentId: number,
        exceptTaskId: number | null,
        removeDuplicatesBy: string | null,
        status: string, 
        shouldFinish = true
    ) {
        const ids = await this.getCompletedChildrenIds(
            parentId,
            exceptTaskId,
        )

        return await this.finishParentTask(ids, parentId, removeDuplicatesBy, status, shouldFinish)
    }

    static async finishParentTask(ids: any[], parentId: number, removeDuplicatesBy: string | null, status: string, shouldFinish: boolean) {
        let [itemsCount, path] = await normalizeAndDeduplicateChildrenTasks(ids, parentId, removeDuplicatesBy)
        const isLarge = isLargeFile(path as any)

        const taskUpdateDetails: any = {
            result_count: itemsCount,
            status: status,
            is_large: isLarge,
        }
        if (shouldFinish) {
            // this flow ran by task deletion/abortuin
            const now_date = new Date()
            taskUpdateDetails['finished_at'] = now_date

        } else {
            // this flow ran by cache completeion
        }

        return this.updateTask(parentId, taskUpdateDetails)
    }

    static async collectAndSaveAllTaskForAbortedTask(
        parentId: number,
        removeDuplicatesBy: string | null,
    ) {
        const ids = await this.getChildrenIdsWithResults(
            parentId,
        )
        return await this.finishParentTask(ids, parentId, removeDuplicatesBy, TaskStatus.ABORTED, true)

    }

    static async readCleanSaveTask(
        parentId: number,
        removeDuplicatesBy: string | null,
        status: string, is_already_large:boolean, 
        extra_updates:any = null
        
    ) {

        const ids = await this.getCompletedChildrenIds(
            parentId,
            null,
        )
        let [itemsCount, path] = await normalizeAndDeduplicateChildrenTasks(ids, parentId, removeDuplicatesBy)
        
        const isLarge = is_already_large ? true:isLargeFile(path as any)
        const finished_at = new Date()
        
        const taskUpdateData = {
            ...(extra_updates ? extra_updates(finished_at) : {}),
            result_count: itemsCount,
            status: status,
            finished_at: finished_at,
            is_large: isLarge,
        }
        const update_result = this.updateTask(parentId, taskUpdateData)
        return update_result;
    }
    static async updateParentTaskResults(parentId: number, result: any[], is_already_large:boolean) {
        if (result && result.length > 0) {
            const path = await TaskResults.appendAllTask(parentId, result);
            const isLarge = is_already_large ? true:isLargeFile(path)

            return new Promise((resolve, reject) => {
                db.update(
                    { id: parentId },
                    { 
                        $set: { is_large: isLarge, },
                        $inc: { result_count: result.length } },
                    {},
                    (err: Error | null) => {
                        if (err) {
                            reject(err);
                        } else {
                            resolve(null);
                        }
                    }
                );
            });
        }
        return null;
    }

    /**
     * Streams child task results to parent task file (without loading into memory).
     * Updates parent's result_count and is_large in the DB.
     */
    static async streamChildToParentResults(childId: number, parentId: number, is_already_large: boolean): Promise<void> {
        const itemCount = await TaskResults.streamTaskToTask(childId, parentId)
        
        if (itemCount > 0) {
            const parentPath = TaskResults.generateTaskFilePath(parentId)
            const isLarge = is_already_large || isLargeFile(parentPath)

            await db.updateAsync(
                { id: parentId },
                { 
                    $set: { is_large: isLarge },
                    $inc: { result_count: itemCount }
                })
        }
    }

    static getTask(taskId: number, inStatus?: string[]): Promise<Task> {
        return new Promise((resolve, reject) => {
            const query: any = { id: taskId };
            if (inStatus) {
                query.status = { $in: inStatus };
            }

            db.findOne(query, (err: Error | null, task: any) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(createTask(task));
                }
            });
        });
    }

    static getTaskWithEntities(
        taskId: number,
        entities: string[]
    ): Promise<any> {
        return new Promise((resolve, reject) => {
            db.findOne(
                { id: taskId },
                createProjection(entities),
                (err: Error | null, task: any) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(createTask(task));
                    }
                }
            );
        });
    }

    static getTasksByIds(taskIds: string[]): Promise<any[]> {
        return new Promise((resolve, reject) => {
            db.find(
                { id: { $in: taskIds } },
                (err: Error | null, tasks: any[]) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(tasks.map(createTask));
                    }
                }
            );
        });
    }
}

export { TaskHelper };