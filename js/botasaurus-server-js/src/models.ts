import Datastore from '@seald-io/nedb';

// Assuming TaskResults is implemented elsewhere
import { TaskResults } from './task-results';
import { db_path, id_path } from './utils'
import './db-setup'
import fs from 'fs';
import { isNullish } from './null-utils'
// Database setup
const db = new Datastore({ filename: db_path, autoload: true , timestampData:true});

// Global ID variable
let globalId: number;

// Extract common function to get largest ID from database
function getLargestIdFromDb(): Promise<number> {
  return new Promise((resolve, reject) => {
    db.find({}).sort({ id: -1 }).limit(1).exec((err, docs) => {
      if (err) {
        reject(err);
        return;
      }
      const largestId = docs.length > 0 ? parseInt(docs[0].id) || 0 : 0;
      resolve(largestId);
    });
  });
}

// Extract function to parse ID from string content
function parseIdFromString(content: string): number | null {
  const id = parseInt(content.trim());
  return isNaN(id) ? null : id;
}

// Extract function to read ID from file
function readIdFromFile(): number | null {
  try {
    const content = fs.readFileSync(id_path, 'utf-8');
    return parseIdFromString(content);
  } catch (error) {
    return null;
  }
}

// Get ID function according to specification
async function getId(): Promise<number> {
  if (!fs.existsSync(id_path)) {
    // File doesn't exist, get largest ID from database
    return getLargestIdFromDb();
  }
  
  // Try to read ID from file
  const fileId = readIdFromFile();
  
  // If we couldn't get a valid ID from file, fall back to database
  if (fileId === null) {
    return getLargestIdFromDb();
  }
  
  return fileId;
}

// Initialize auto increment database
async function initAutoIncrementDb() {
  globalId = await getId();
  
  // @ts-ignore
  db.getAutoincrementId = () => {
    globalId = globalId + 1;
    fs.writeFileSync(id_path, globalId.toString());
    return globalId;
  };
}
// @ts-ignore
const getAutoincrementId = () => db.getAutoincrementId()
// Create indexes
db.ensureIndex({ fieldName: 'id', unique:true });
db.ensureIndex({ fieldName: 'status' });
db.ensureIndex({ fieldName: 'sort_id',});
// db.ensureIndex({ fieldName: 'task_name' }); // can add later
// db.ensureIndex({ fieldName: 'scraper_name' }); // can add later
db.ensureIndex({ fieldName: 'scraper_type' });
db.ensureIndex({ fieldName: 'is_all_task' });
db.ensureIndex({ fieldName: 'is_sync' });

const TaskStatus = {
    PENDING: 'pending',
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed',
    FAILED: 'failed',
    ABORTED: 'aborted',
  } as const;
  

// Utility functions
function removeDuplicatesByKey(dictList: any[], key: string): any[] {
    const seen = new Set();
    const newDictList: any[] = [];
    for (const d of dictList) {
      if (key in d && !isNullish(d[key])) {
        if (!seen.has(d[key])) {
          seen.add(d[key]);
          newDictList.push(d);
        }
      } else {
        newDictList.push(d);
      }
    }
    return newDictList;
  }
    
  function calculateDuration(obj: Task): number | null {
    if (obj.started_at) {

      const endTime = obj.finished_at || new Date();
      const duration = (endTime.getTime() - obj.started_at.getTime()) / 1000;
  
      if (duration === 0) {
        return 0;
      }
  
      const result = parseFloat(duration.toFixed(2));
  
      return result;
    }
  
    return null;
  }
  
function isoformat(obj: Date | null | undefined): string | null {
    return obj ? obj.toISOString() : null;
}



export function createTaskName(taskName:any, taskId:any) {
  return taskName !== null ? taskName : `Task ${taskId}`;
}
function serializeUiOutputTask(obj: Task, _: any): any {
    const taskId = obj.id;
  
    return {
      id: taskId,
      status: obj.status,
      task_name: createTaskName(obj.task_name, taskId),
      result_count: obj.result_count,
      is_all_task: obj.is_all_task,
      started_at: isoformat(obj.started_at),
      finished_at: isoformat(obj.finished_at),
    };
  }
  
function serializeUiDisplayTask(obj: Task): Partial<Task> {
    return {
        scraper_name: obj.scraper_name,
        status: obj.status,
        is_large: obj.is_large,
        updated_at: obj.updated_at,
    };
}


export function serializeTaskForRunTask(obj: Task){
  const taskId = obj.id;
  const status = obj.status;

  return {
    id: taskId,
    status: status,
    scraper_name: obj.scraper_name,
    scraper_type: obj.scraper_type,
    is_all_task: obj.is_all_task,
    is_sync: obj.is_sync,
    is_large: obj.is_large,
    parent_task_id: obj.parent_task_id,
    data: obj.data,
    metadata: obj.meta_data,
    result_count: obj.result_count,
  };
}
async function serializeTask(obj: Task, withResult: boolean): Promise<any> {
  const taskId = obj.id;
  const status = obj.status;
  let result = {};

  if (withResult) {
    result = await fetchTaskResult(status, result, obj, taskId)
  }
  return {
    id: taskId,
    status: status,
    task_name: createTaskName(obj.task_name, taskId),
    scraper_name: obj.scraper_name,
    scraper_type: obj.scraper_type,
    is_all_task: obj.is_all_task,
    is_sync: obj.is_sync,
    is_large: obj.is_large,
    parent_task_id: obj.parent_task_id,
    duration: calculateDuration(obj),
    started_at: isoformat(obj.started_at),
    finished_at: isoformat(obj.finished_at),
    data: obj.data,
    metadata: obj.meta_data,
    ...result,
    result_count: obj.result_count,
    created_at: isoformat(obj.created_at),
    updated_at: isoformat(obj.updated_at),
  };
}
// Task model
class Task {
    id!: number;
    status!: string;
    sort_id!: number;
    task_name!: string;
    scraper_name!: string;
    scraper_type!: string;
    is_all_task!: boolean;
    is_sync!: boolean;
    is_large?: boolean;
    parent_task_id!: number | null;
    started_at!: Date | null;
    finished_at!: Date | null;
    data!: any;
    meta_data!: any;
    result_count!: number;
    created_at!: Date;
    updated_at!: Date;
    result?: any;
  
    constructor(data: Partial<Task>) {
      Object.assign(this, data);
    }
  
    toJson(withResult=true) {
      return serializeTask(this, withResult);
    }
  }
  const createTask = (x:any) => {
    if (isNullish( x)) {
      // @ts-ignore typing fix
      return null as Task;
    }
  

    return new Task(x)
  }
  export { getAutoincrementId, createTask, db, Task, TaskStatus, removeDuplicatesByKey, calculateDuration, isoformat, serializeUiOutputTask, serializeUiDisplayTask, serializeTask , initAutoIncrementDb};



export function isFailedAndNonAllTask(status: any, is_all_task: any) {
  return status === TaskStatus.FAILED && !is_all_task
}

async function fetchTaskResult(status: string, result: {}, obj: Task, taskId: number) {
  if (status === TaskStatus.PENDING) {
    result = { result: null }
  } else if (status !== TaskStatus.IN_PROGRESS || obj.is_all_task) {
    if (isFailedAndNonAllTask(status, obj.is_all_task)) {
      const taskResult = await TaskResults.getTask(taskId) as any
      result = { result: taskResult[0] }
    } else {
      result = {
        result: await TaskResults.getTask(taskId),
      }
    }

  } else {
    result = { result: null }
  }
  return result
}
