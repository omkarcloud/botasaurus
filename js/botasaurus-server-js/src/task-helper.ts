import * as fs from 'fs';
import { isNotNullish, isNullish } from "./null-utils";
import { createTask, db, Task } from "./models";
import { TaskResults } from "./task-results";
import { TaskStatus } from "./models";
import { NDJSONWriteStream } from "./ndjson"
import { isLargeFile } from './utils'
import { sleep } from 'botasaurus/utils'
import { normalizeItem } from 'botasaurus/output'

export function createProjection(ets: string[]) {
    return ets.reduce((acc: any, field) => {
        acc[field] = 1;
        return acc;
    }, {});
}


function populateMissingKeys(newKeys: string[], allKeysMapping: any) {
    for (const key of newKeys) {
        if (!(key in allKeysMapping)) {
            allKeysMapping[key] = null
        }
    }
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

async function normalizeAndDeduplicateChildrenTasks(ids: number[], parentId:number, removeDuplicatesBy: string | null) {
        let itemsCount = 0
        let allKeysMapping: any = null
        let allKeys: any = null
        let firstItemKeyCount = 0
        const taskFilePath = TaskResults.generateTaskFilePath(parentId)

        // First pass: collect all unique keys from all objects
        await TaskResults.streamMultipleTask(ids, (item) => {
            const itemKeys = Object.keys(item)
            
            if (allKeysMapping === null) {
                // First item: initialize with its keys
                allKeysMapping = createKeyToNullMapping(item)
                firstItemKeyCount = itemKeys.length
            } else {
                const currentKeyCount = Object.keys(allKeysMapping).length
                
                if (itemKeys.length !== currentKeyCount) {
                    // Different number of keys - collect new ones
                    populateMissingKeys(itemKeys, allKeysMapping)
                } else {
                    // Same number of keys, but check if there are any new keys (different keys, not just different order)
                    for (const key of itemKeys) {
                        if (!(key in allKeysMapping)) {
                            // Found a new key, collect all keys from this item
                            populateMissingKeys(itemKeys, allKeysMapping)
                            break
                        }
                    }
                }
            }
        })

        // After first pass, get the complete list of all keys
        if (allKeysMapping !== null) {
            allKeys = Object.keys(allKeysMapping)
        }

        const shouldNormalize = allKeys && allKeys.length !== firstItemKeyCount

        const tempfile = taskFilePath + '.temp'
        const ndjsonWriteStream = new NDJSONWriteStream(tempfile)
        const seen = new Set()
        try {
            await TaskResults.streamMultipleTask(ids, async (item) => {
                if (shouldNormalize) {
                    item = normalizeItem(allKeys, item)
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
            await moveFile(tempfile, taskFilePath)
        } catch (error) {
            console.error('Error occurred while processing tasks:', error)
            await ndjsonWriteStream.end()
            throw error
        }
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
        };

        if (exceptTaskId) {
            query.id = { $ne: exceptTaskId };
        }

        const results = await new Promise<any[]>((resolve, reject) => {
            db.find(query).sort({ sort_id: -1}).exec((err: any, docs: any[]) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(docs.map((doc) => doc.id));
                }
            })
        });
        
        return results
       
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
        return new Promise((resolve, reject) => {
            db.update(
                { id: taskId, finished_at: null },
                { $set: { finished_at: now } },
                {},
                (err: any, _: any) => {
                    if (err) {
                        reject(err);
                    } else {
                        this.updateTask(taskId, { status: TaskStatus.ABORTED })
                            .then(resolve)
                            .catch(reject);
                    }
                }
            );
        });
    }

    static async abortChildTasks(taskId: number): Promise<number> {
        const now = new Date();
        await new Promise((resolve, reject) => {
            db.update(
                { parent_task_id: taskId, finished_at: null },
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
        return await new Promise((resolve, reject) => {
            db.update(
                { parent_task_id: taskId },
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
        let [itemsCount, path] = await normalizeAndDeduplicateChildrenTasks(ids, parentId, removeDuplicatesBy)
        const isLarge = isLargeFile(path as any)

        const taskUpdateDetails:any = {
            result_count: itemsCount,
            status: status,
            is_large: isLarge,
        }
        if (shouldFinish) {
            // this flow ran by task deletion/abortuin
            const now_date = new Date()
            taskUpdateDetails['finished_at'] =  now_date

            return this.updateTask(parentId, taskUpdateDetails)
            // const query = {
            //     $and: [
            //         { id: parentId },
            //         { started_at: null },
            //     ]
            // }
            // const update = {
            //     "started_at": now_date
            // }
            
            // const updateResult = await this.updateTaskByQuery(query, update)
            // console.log({query, update, updateResult, })
            // return updateResult

        } else {
            // this flow ran by cache completeion
            return this.updateTask(parentId, taskUpdateDetails);
        }
        

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