import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { rmSync } from 'fs';

import { createDirectoryIfNotExists } from './decorators-utils';
import { readJson, relativePath, writeJson as formatWriteJson } from './utils';
import { DontCache } from './dontcache';
import { prompt } from './beep-utils'

class CacheMissException extends Error {
  constructor(public key: string) {
    super(`Cache miss for key: '${key}'`);
  }
}

function writeJson(data: any, path: string): void {
  fs.writeFileSync(path, JSON.stringify(data),  { encoding: "utf-8" });
}

function getFnName(func: Function | string): string {
  return typeof func === 'string' ? func : func.name;
}

function _getCachePath(func: Function | string, data: any): string {
  const fnName = getFnName(func);

  const serializedData = JSON.stringify(data);
  const dataHash = crypto.createHash('md5').update(serializedData).digest('hex');
  const cachePath = path.join(Cache.cacheDirectory, fnName, `${dataHash}.json`);
  return cachePath;
}

function _hash(data: any): string {
  const serializedData = JSON.stringify(data);
  return crypto.createHash('md5').update(serializedData).digest('hex');
}

function _has(cachePath: string): boolean {
  return fs.existsSync(cachePath);
}

function _get(cachePath: string): any {
  try {
    return readJson(cachePath);
  } catch (error) {
    _remove(cachePath);
    throw new CacheMissException(cachePath);
  }
}

function safeGet(cachePath: string): any {
  try {
    return readJson(cachePath);
  } catch (error) {
    _remove(cachePath);
    return null;
  }
}

function _readJsonFiles(filePaths: string[]): any[] {
  return filePaths.map(safeGet);
}

function _remove(cachePath: string): void {
  if (fs.existsSync(cachePath)) {
    try {
      fs.unlinkSync(cachePath);
    } catch (error) {
      console.error("faced error while removing")
      console.error(error)
      // Ignore error
    }
  }
}

function _deleteItems(filePaths: string[]): void {
  filePaths.forEach(_remove);
}

function rstrip_json(str:string) {
    return str.endsWith('.json') ? str.slice(0, -5) : str;
}

function getFilesWithoutJsonExtension(directoryPath: string): string[] {
  if (!fs.existsSync(directoryPath)) {
    return [];
  }

  const files = fs.readdirSync(directoryPath);
  return files.map(rstrip_json);
}

function isAffirmative(inputString: string): boolean {
  const affirmativeValues = new Set(['true', 'yes', 'y', '1', 'yeah', 'yep', 'sure', 'ok', 'okay', 'affirmative', 't']);
  const normalizedString = inputString.trim().toLowerCase();
  return affirmativeValues.has(normalizedString);
}

function isNegative(inputString: string): boolean {
  const negativeValues = new Set(['false', 'no', 'n', '0', 'nah', 'nope', 'never', 'negative', 'f']);
  const normalizedString = inputString.trim().toLowerCase();
  return negativeValues.has(normalizedString);
}

const createdFns = new Set<string>();
let cacheCheckDone = false;

function _createCacheDirectoryIfNotExists(func?: Function | string): void {
  if (!cacheCheckDone) {
    cacheCheckDone = true;
    createDirectoryIfNotExists(Cache.cacheDirectory);
  }

  if (func !== undefined) {
    const fnName = getFnName(func);
    if (!createdFns.has(fnName)) {
      createdFns.add(fnName);
      const fnCacheDir = path.join(Cache.cacheDirectory, fnName);
      createDirectoryIfNotExists(fnCacheDir);
    }
  }
}

function getCachedFiles(func: Function | string): string[] {
  const fnName = getFnName(func);
  const fnCacheDir = path.join(Cache.cacheDirectory, fnName);;
  const cacheDir = fnCacheDir;
  return getFilesWithoutJsonExtension(cacheDir);
}

class Cache {
  static cacheDirectory = relativePath('cache');
  static REFRESH = 'REFRESH';

  static setCacheDirectory(folder: string): void {
    // replaces end '/'
    Cache.cacheDirectory = folder.replace(/\/$/, '') + '/';
  }

  static put(func: Function | string, keyData: any, data: any): void {
    _createCacheDirectoryIfNotExists(func);
    const path = _getCachePath(func, keyData);
    writeJson(data, path);
  }

  static hash(data: any): string {
    return _hash(data);
  }

  static has(func: Function | string, keyData: any): boolean {
    _createCacheDirectoryIfNotExists(func);
    const path = _getCachePath(func, keyData);
    return _has(path);
  }

  static get(func: Function | string, keyData: any, raiseException = true): any {
    if (Array.isArray(keyData)) {
      return Cache.getItems(func, keyData);
    }

    _createCacheDirectoryIfNotExists(func);
    const path = _getCachePath(func, keyData);
    if (_has(path)) {
      try {
        return _get(path);
      } catch (error) {
        return null;
      }
    }

    if (raiseException) {
      throw new CacheMissException(path);
    }
    return null;
  }

  static getItems(func: Function | string, items?: any[]): any[] {
    if (typeof items === 'string') {
      return Cache.getItems(func, [items]);
    }

    const hashes = Cache.getItemsHashes(func, items);
    const fnName = getFnName(func);
    const paths = hashes.map(r => path.join(Cache.cacheDirectory, fnName, `${r}.json`));
    return _readJsonFiles(paths);
  }

  static getItemsHashes(func: Function | string, items?: any[]): string[] {
    const results = getCachedFiles(func);

    if (items === undefined) {
      return results;
    } else {
      const itemSet = new Set(items.map(Cache.hash));
      return results.filter(r => itemSet.has(r));
    }
  }

  static delete(func: Function | string, keyData: any): void {
    _createCacheDirectoryIfNotExists(func);
    const path = _getCachePath(func, keyData);
    _remove(path);
  }

  static deleteItems(func: Function | string, items: any[]): number {
    const hashes = Cache.getItemsHashes(func, items);
    const fnName = getFnName(func);
    const paths = hashes.map(r => path.join(Cache.cacheDirectory, fnName, `${r}.json`));
    _deleteItems(paths);
    return hashes.length;
  }

  static clear(func?: Function | string): void {
    if (func !== undefined) {
      const fnName = getFnName(func);
      const fnCacheDir = path.join(Cache.cacheDirectory, fnName);;
      const cacheDir = fnCacheDir;
      if (fs.existsSync(cacheDir)) {
        rmSync(cacheDir, { recursive: true, force: true });
      }
      createdFns.delete(fnName);
    } else {
      const cacheDir = Cache.cacheDirectory;
      if (fs.existsSync(cacheDir)) {
        rmSync(cacheDir, { recursive: true, force: true });
      }
      cacheCheckDone = false;
      createdFns.clear();
    }
  }

  static async deleteItemsByFilter(func: Function | string, items: any[], shouldDeleteItem: (key: any, data: any) => boolean): Promise<number> {
    const testItems = Cache.filterItemsInCache(func, items);
    const collectedHoneypots: any[] = [];

    for (const key of testItems) {
      try {
        const data = Cache.get(func, key);
        if (shouldDeleteItem(key, data)) {
          collectedHoneypots.push(key);
        }
      } catch (error) {
        // Ignore error
      }
    }

    if (collectedHoneypots.length > 0) {
      const path = './output/items_to_be_deleted.json';
      formatWriteJson(collectedHoneypots, path);
      while (true) {
        const result = await prompt(`Should we delete ${collectedHoneypots.length} items in ${path}? (Y/n): `);

        if (isAffirmative(result)) {
          console.log(`Deleting ${collectedHoneypots.length} items...`);
          Cache.deleteItems(func, collectedHoneypots);
          break;
        } else if (isNegative(result)) {
          console.log('No items were deleted');
          break;
        }
      }
    } else {
      console.log('No items were deleted');
    }

    return collectedHoneypots.length;
  }

  static filterItemsInCache(func: Function | string, items: any[]): any[] {
    const cachedItems = new Set(Cache.getItemsHashes(func));
    return items.filter(item => cachedItems.has(Cache.hash(item)));
  }

  static filterItemsNotInCache(func: Function | string, items: any[]): any[] {
    const cachedItems = new Set(Cache.getItemsHashes(func));
    return items.filter(item => !cachedItems.has(Cache.hash(item)));
  }

  static printCachedItemsCount(func: Function | string): number {
    const cachedItemsCount = getCachedFiles(func).length;
    const nm = getFnName(func);
    console.log(`Number of cached items for ${nm}: ${cachedItemsCount}`);
    return cachedItemsCount;
  }

  static getCachedItemsCount(func: Function | string): number {
    return getCachedFiles(func).length;
  }
}


export {
  CacheMissException,
  writeJson,
  getFnName,
  safeGet,
  getFilesWithoutJsonExtension,
  getCachedFiles,
  Cache, 
  DontCache,
  _createCacheDirectoryIfNotExists as createCacheDirectoryIfNotExists,
  _getCachePath, 
  _has,
  _get,
  _remove,
  _deleteItems,
  readJson,
  _readJsonFiles, 
  _hash,
  isAffirmative,
};