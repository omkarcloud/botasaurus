import * as fs from 'fs';
import { totalmem } from 'os';
import * as path from 'path';
import {isMaster} from './env';
import { getTargetDirectoryPath } from './paths'
import { getBotasaurusStorage } from 'botasaurus/botasaurus-storage'

function getTotalMemory() {
  let mem = getBotasaurusStorage().getItem("memory")
  if (!mem) {
      mem = totalmem()
      getBotasaurusStorage().setItem("memory", mem);
  }
  return mem;
}

const targetDirectory = getTargetDirectoryPath()

function getPath(...paths: string[]): string {
  if (isMaster) {
    return path.join(targetDirectory, '..', 'db', ...paths);
  } else {
    return path.join(targetDirectory, ...paths);
  }
}


const pathTaskResults = getPath('task_results');
const pathTaskResultsTasks = getPath( 'task_results', 'tasks');
const pathTaskResultsCache = getPath( 'task_results', 'cache');
const pathTaskResultsCacheDirect = getPath( 'task_results', 'direct_cache');
const cacheStoragePath = getPath( 'task_results', 'cache_storage.json');
const id_path = getPath('task_results', 'last_task_id.txt');
const db_path = getPath('db.nedb');

function isNotEmptyObject(obj: object): boolean {
  return Object.keys(obj).length > 0;
}

function isEmptyObject(obj: object): boolean {
  return Object.keys(obj).length === 0;
}

function isObject(value: any): value is Record<string, any> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function callOnce(fn: Function): Function {
  let called = false;
  return function(...args: any[]) {
    if (!called) {
      called = true;
      return fn(...args);
    }
  };
}
// 800 MB = 800 * 1024 * 1024 bytes
const MAX_SIZE_LIMIT = 800 * 1024 * 1024;
// const MAX_SIZE_LIMIT = 10 * 1024 * 1024;

const FIVE_GB = 5 * 1024 * 1024 * 1024;
const FOUR_HUNDRED_MB = 400 * 1024 * 1024;

function isLargeFile(filePath:string) {
  try {
      // Get file stats
      const stats = fs.statSync(filePath);
      // Compare file size with limit
      if(stats.size > MAX_SIZE_LIMIT){
        return true
      }

      if (stats.size > FOUR_HUNDRED_MB && getTotalMemory() < FIVE_GB) {
        return true;
      }

      return false;
  } catch (err) {
      console.error(err);
      return false;
  }
}

function isEmpty(x: any) {
  return (
    x === null ||
    x === undefined ||
    (typeof x == 'string' && x?.trim() === '') || 
    isEmptyObject(x)
  )
}


// Helper to normalize path similar to Python's os.path.normpath
function normalizePath(path: string): string {
  return path
    .split("/")
    .filter(Boolean)
    .join("/")
    .replace(/\/+/g, "/");
}

function cleanBasePath(apiBasePath: string | null | undefined){
  
  if (typeof apiBasePath === "string") {
    let path = apiBasePath ? normalizePath(apiBasePath) : "";

    if (path === ".") {
      path = "";
    } else if (path) {
      if (!path.startsWith("/")) {
        path = "/" + path;
      }
      if (path.endsWith("/")) {
        path = path.slice(0, -1);
      }
    }

    return path;
  }
  return ''

}
const negativeValues = new Set(["false", "no", "n", "0", "nah", "nope", "never", "negative", "f"]);
const affirmativeValues = new Set(["true", "yes", "y", "1", "yeah", "yep", "sure", "ok", "okay", "affirmative", "t"]);

const parseBoolean = (value:any) => {
  if (typeof value === 'string') {

        const normalizedValue = value.trim().toLowerCase();
        if (negativeValues.has(normalizedValue)) {
          return false;
        }
        if (affirmativeValues.has(normalizedValue)) {
          return true;
        }
  }
  return null;
}

export { parseBoolean, callOnce, db_path, id_path, pathTaskResults, pathTaskResultsTasks, pathTaskResultsCacheDirect,pathTaskResultsCache ,cacheStoragePath, isNotEmptyObject,isEmpty,  isObject, isEmptyObject, targetDirectory, isLargeFile, cleanBasePath};