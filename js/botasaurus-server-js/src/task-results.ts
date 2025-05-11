import {  writeFileSync, readdirSync, copyFile } from 'fs';
import { join } from 'path';
import {  pathTaskResultsTasks,  pathTaskResultsCache, cacheStoragePath, isLargeFile, pathTaskResultsCacheDirect } from './utils';
import { _readJsonFiles, _has,_remove, _deleteItems, _hash, readJson} from 'botasaurus/cache';
import { LocalStorage } from 'botasaurus/botasaurus-storage';
import { appendNdJson, readNdJson, readNdJsonCallback, writeNdJson } from './ndjson'
import { writeJson } from 'botasaurus/utils'


let _storage: LocalStorage | null = null;

function getCacheStorage(): LocalStorage {
    if (!_storage) {
        _storage = new LocalStorage(cacheStoragePath);
    }
    return _storage;
}
function _getNdTask(id: number, limit?: number|null){
  const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
  if (!_has(taskPath)) {
    return null;
  }
  return readNdJson(taskPath, limit);
}

export function createCacheKey(scraperName: string, data: any): string {
  return `${scraperName}-${_hash(data)}.ndjson`;
}


function getFiles(): string[] {
  return readdirSync(pathTaskResultsCache);
}


function doCopyFile(fromPath: string, toPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    copyFile(fromPath, toPath, (copyErr:any) => {
      if (copyErr) {
          reject(copyErr);
      } else {
          resolve();
      }
  });
  });
}


async function computeItemDetails(cache_key: string ) {
  let count = 0
  const incrementItemCount: any = () => {
    count++
  }
  const taskResultsFilePath = join(pathTaskResultsCache, cache_key)
  await readNdJsonCallback(taskResultsFilePath, incrementItemCount)

  const isLarge = isLargeFile(taskResultsFilePath)

  return  { "count": count, "isLarge": isLarge }
}


export class DirectCallCacheService {

  static createCacheKey(scraperName: string, data: any): string {
    return  `${scraperName}-${_hash(data)}.json`;
  }

  static has(key: string): boolean {
    const pt = DirectCallCacheService.createCachedItemPath(key);
    return _has(pt);
  }

  static createCachedItemPath(key: string): string {
    return join(pathTaskResultsCacheDirect, key);
  }

  static get(key: string): any {
    const pt = DirectCallCacheService.createCachedItemPath(key);
    try {
      return readJson(pt).data;
    } catch (error) {
      _remove(pt);
      throw new Error(`File is corrupted at path: ${pt}`);
    }
  }

  static remove(key: string): void {
    const pt = DirectCallCacheService.createCachedItemPath(key);
    _remove(pt);
  }

  static put(key: string, item: any): void {
    const pt = DirectCallCacheService.createCachedItemPath(key);
    writeJson({ data: item }, pt, null as any);
  }
}

export class TaskResults {
  static filterItemsInCache(items: string[]): string[] {
    const cachedItems = new Set(getFiles());
    return items.filter((item) => cachedItems.has(item));
  }

  static saveCachedTask(scraperName: string, data: any, result: any,isLarge:boolean) {
    const cache_key = createCacheKey(scraperName, data);
    const taskPath = join(pathTaskResultsCache, cache_key);
    // can save islarge metric as well.
    getCacheStorage().setItem(cache_key, {"count":result.length, "isLarge":isLarge})
    return writeNdJson(result, taskPath);
  }

static async getCachedItemDetails(cache_key: string) {
    let item:{
      count: number;
      isLarge: boolean;
  } = getCacheStorage().getItem(cache_key);
    if (item === null) {
        item = await computeItemDetails(cache_key)
        getCacheStorage().setItem(cache_key, item);
    }
    return item;
}
static saveTask(id: number, data: any){
  const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
  return writeNdJson(data, taskPath);
}

  static cloneTaskFromCacheKey(id: number, cache_key: string){
    const fromPath = join(pathTaskResultsCache, cache_key);
    const targetPath = join(pathTaskResultsTasks, `${id}.ndjson`)
    
    return doCopyFile(fromPath, targetPath);
  }

  static getTask(id: number, limit?: number|null){
    return _getNdTask(id, limit);
  }

  static deleteTask(id: number): void {
    _remove(join(pathTaskResultsTasks, `${id}.ndjson`));
  }

  static deleteTasks(ids: number[]): void {
    _deleteItems(ids.map((id) => join(pathTaskResultsTasks, `${id}.ndjson`)));
  }

  // // increase efficiency
  // static getAllTask(id: number, limit?: number|null){
  //   const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
  //   if (!_has(taskPath)) {
  //     return null;
  //   }
  //   return readNdJson(taskPath, limit)
  // }
  static taskExists(id: number){
    const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
    if (!_has(taskPath)) {
      return false;
    }
    return true;
  }  
  
  static streamTask(id: number, onData: (item: any, index:number) =>any, limit?: number|null){
    const taskPath = TaskResults.generateTaskFilePath(id);
    if (!_has(taskPath)) {
      return 0;
    }
    return readNdJsonCallback(taskPath, onData, limit)
  }

  static async streamMultipleTask(ids: number[], onData: (item: any) => any) {
    for (const id of ids) {
      const taskPath = TaskResults.generateTaskFilePath(id);
      if (_has(taskPath)) {
        await readNdJsonCallback(taskPath, onData);
      }
    }
  }

  static generateTaskFilePath(id: number) {
    return join(pathTaskResultsTasks, `${id}.ndjson`)
  }

  static appendAllTask(id: number, data: any[]) {
    const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
    if (!data) {
      if (!_has(taskPath)) {
        writeFileSync(taskPath, '',{ encoding: 'utf-8' });
      }
      return taskPath;
    }
    return appendNdJson(data, taskPath)
  }

  static deleteAllTask(id: number): void {
    const taskPath = join(pathTaskResultsTasks, `${id}.ndjson`);
    _remove(taskPath);
  }
}