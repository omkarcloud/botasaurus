import * as fs from 'fs';
import * as path from 'path';
import {isMaster} from './env';
import { getTargetDirectoryPath } from './paths'

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
function isLargeFile(filePath:string) {
  // return true
  try {
      // Get file stats
      const stats = fs.statSync(filePath);
      // Compare file size with limit
      return stats.size > MAX_SIZE_LIMIT;
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

// @ts-ignore
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

}

export { callOnce, db_path, pathTaskResults, pathTaskResultsTasks, pathTaskResultsCacheDirect,pathTaskResultsCache ,cacheStoragePath, isNotEmptyObject,isEmpty,  isObject, isEmptyObject, targetDirectory, isLargeFile, cleanBasePath};