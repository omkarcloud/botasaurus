import * as fs from 'fs';
import readline from 'readline'
import { _readJsonFiles, _has,_remove, _deleteItems, _hash } from 'botasaurus/cache';
import { appendOutputIfNeeded } from 'botasaurus/output';
import { isNotNullish } from './null-utils'
import { stringify } from 'csv-stringify/sync'

export class NDJSONWriteStream {
  private writeStream: fs.WriteStream;
  private error: Error | null = null;
  private rejectWaiting = new Set<(error: Error) => void>();

  constructor(filePath: string, append = false) {
      if (append) {
          this.writeStream = fs.createWriteStream(filePath, {
              flags: 'a',
              encoding: 'utf-8',
              highWaterMark: 64 * 1024 // 64 KB, you can adjust this value as needed

            });            
      } else {
          this.writeStream = fs.createWriteStream(filePath, {
              encoding: 'utf-8',
              highWaterMark: 64 * 1024 // 64 KB, you can adjust this value as needed
            });
      }
      // A stream's failure (a file locked by Excel, a full disk) is an 'error'
      // event. With no listener it was an uncaught exception, and the app shuts
      // down on those: exporting over a CSV open in Excel closed the whole app,
      // running tasks included (2026-10-31 test). It now rejects the writes.
      this.writeStream.on('error', (error) => {
        this.error = error;
        for (const reject of this.rejectWaiting) {
          reject(error);
        }
        this.rejectWaiting.clear();
      });
  }

  async push(data: any): Promise<void> {
    return this.performWrite(JSON.stringify(data) + '\n');
  }

   performWrite(content: any): void | PromiseLike<void> {
    return new Promise((resolve, reject) => {
      if (this.error) {
        return reject(this.error);
      }
      if (!this.writeStream.write(content)) {
        const done = () => {
          this.rejectWaiting.delete(rejectWrite);
          resolve() // Resolve the promise if write is successful
        };
        const rejectWrite = (error: Error) => {
          this.writeStream.off('drain', done);
          reject(error);
        };
        this.rejectWaiting.add(rejectWrite);
        this.writeStream.once('drain', done)
      } else {
        resolve() // Resolve the promise if write is successful
      }
    })
  }

  // After a failed export: closes the file without finishing it
  destroy() {
    this.writeStream?.destroy();
  }

  end(): Promise<void> {
    if (!this.writeStream){
      return Promise.resolve()
    }
    return new Promise(async (resolve, reject) => {
      if (this.error) {
        return reject(this.error);
      }
      this.rejectWaiting.add(reject);
      try {
        await this.preEnd()
      } catch (error) {
        return reject(error);
      }
      if (this.error) {
        return reject(this.error);
      }
      this.writeStream.end((error?: Error | null) => {
        this.rejectWaiting.delete(reject);
        if (error || this.error) {
          return reject(this.error ?? error);
        }
        resolve(); // Resolve when the stream is finished
        // @ts-ignore
        this.writeStream = null
      });
    });
  }

  async preEnd() {
    // Add any necessary pre-end logic here
  }
   async preStart() {
    // Add any necessary pre-end logic here
  }

}

export class JSONWriteStream extends NDJSONWriteStream {
  private sep: string;

  constructor(filePath: string) {
    super(filePath, false); // append will always be false
    this.sep = "";
  }
  override async preStart() {
    await this.performWrite('[');
  }

  override async push(data: any): Promise<void> {
    const content = this.sep + JSON.stringify(data);
    if (!this.sep) {
      this.sep = ",";
    }
    return this.performWrite(content);
  }

  override async preEnd() {
    await this.performWrite(']');
  }
}

export class CSVWriteStream extends NDJSONWriteStream {
  constructor(filePath: string) {
    super(filePath, false); // append will always be false
  }

  // @ts-ignore
  override async preStart(headers: string[]) {
    const headerLine = stringify([headers]);
    await this.performWrite(headerLine);
  }

  override async push(data: string[]): Promise<void> {
    const content = stringify([data]);
    return this.performWrite(content);
  }
}
export function readNdJson(taskPath: string, limit: number | null | undefined=null) : Promise<any[]>{
    const items: any[] = []
  
    const fileStream = fs.createReadStream(taskPath, { encoding: 'utf-8' })
    let lineNumber = 0
  
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity,
    })
  
    rl.on('line', (line: string) => {
      lineNumber++
      // rl.close() still delivers the rest of the chunk it has read
      // @ts-ignore
      if (isNotNullish(limit) && items.length >= limit) {
        return
      }
  
      line = line.trim()
      if (line !== '') {
        try {
          const item = JSON.parse(line)
          items.push(item)
        } catch (error) {
          // Handle potential malformed JSON
          const splitLines = line.split('}{')
  
          for (let i = 0; i < splitLines.length; i++) {
            const splitLine = splitLines[i]
            try {
              let parsedItem
              if (i % 2 === 0) {
                // Even index (including 0)
                parsedItem = JSON.parse(splitLine + '}')
              } else {
                // Odd index
                parsedItem = JSON.parse('{' + splitLine)
              }
              items.push(parsedItem)
            } catch (error) {
              console.log(`Failed to parse line ${lineNumber}, part: ${splitLine}`)
            }
          }
  
        }
        // @ts-ignore
        if (isNotNullish(limit) && items.length >= limit) {
          rl.close()
        }
      }
    })
  
    return new Promise((resolve, reject) => {
      // Unlistened, a file that can't be read (held by security or backup software)
      // was an uncaught exception, and the app shuts down on those
      // (readline passes the stream's error on, and throws it with no listener too)
      fileStream.on('error', reject)
      rl.on('error', reject)
      rl.on('close', () => {
        fileStream.destroy()
        // @ts-ignore
        if (isNotNullish(limit) && items.length > limit) {
          // @ts-ignore
          resolve(items.slice(0, limit))
        } else {
          resolve(items)
        }
      })
    })
  }
  

  export async function writeNdJson(data: any[], taskPath: string) {
    const ndjsonWriteStream = new NDJSONWriteStream(taskPath)
    try {
      for (const item of data) {
        await ndjsonWriteStream.push(item);
      }
    } finally {
      await ndjsonWriteStream.end();
    }
    return taskPath
  }
  
export async function appendNdJson(data: any[], taskPath: string) {
  const ndjsonWriteStream = new NDJSONWriteStream(taskPath, true)
  try {
    for (const item of data) {
      await ndjsonWriteStream.push(item);
    }
  } finally {
    await ndjsonWriteStream.end();
  }  
  return taskPath
}
  
export async function readNdJsonCallback(taskPath: string, onData: (item: any, index: number) => void | false | Promise<void | false>, limit: number | null | undefined = null): Promise<{processedItems: number, hasExited: boolean}> {
  const fileStream = fs.createReadStream(taskPath, { encoding: 'utf-8' });
  let lineNumber = 0;
  let processedItems = 0;
  let isLimitReached = false
  let hasExited = false
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });
  // Unlistened, a file that can't be read (held by security or backup software)
  // was an uncaught exception, and the app shuts down on those
  let readError = null as Error | null;
  const onReadError = (error: Error) => {
    readError = error;
    rl.close();
  };
  fileStream.on('error', onReadError);
  // (readline passes the stream's error on, and throws it with no listener too)
  rl.on('error', onReadError);

  try {
    for await (const line of rl) {
      lineNumber++;
      const trimmedLine = line.trim();
      if (trimmedLine !== '') {
        try {
          const item = JSON.parse(trimmedLine);

          let result;
          try {
            result = await onData(item, processedItems);
          } catch (error: any) {
            error.isOnDataError = true;
            throw error;
          }
          processedItems++;
          if (result === false) {
            hasExited = true
            break;
          }
        } catch (error: any) {
          if (error.isOnDataError) {
            throw error;
          }
          // Handle potential malformed JSON
          const splitLines = trimmedLine.split('}{');

          for (let i = 0; i < splitLines.length; i++) {
            const splitLine = splitLines[i];
            try {
              let parsedItem;
              if (i % 2 === 0) {
                // Even index (including 0)
                parsedItem = JSON.parse(splitLine + '}');
              } else {
                // Odd index
                parsedItem = JSON.parse('{' + splitLine);
              }
              const result = await onData(parsedItem, processedItems);
              processedItems++;
              if (result === false) {
                hasExited = true
                break;
              }
            } catch (error) {
              console.log(`Failed to parse line ${lineNumber}, part: ${splitLine}`);
            }
          }
          if (hasExited) {
            break;
          }
        }
        
        // @ts-ignore
        isLimitReached = isNotNullish(limit) && processedItems >= limit
        
        if (isLimitReached) {
          break;
        }
      }
    }
  } finally {
    rl.close();
    // rl.close() leaves the file open: every page of a file bigger than the read
    // buffer kept a handle until the app closed
    fileStream.destroy();
  }

  if (readError) {
    throw readError;
  }

  if (isLimitReached) {
    // @ts-ignore
    processedItems = limit
  }  
  return {processedItems, hasExited}
}


function fixNdjsonFilename(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.ndjson')) {
    filename = filename + '.ndjson'
  }
  return filename
}

/**
 * Reads an NDJSON file and calls the provided callback for each item.
 * 
 * @param filename - Path to the NDJSON file (will auto-append .ndjson if missing)
 * @param onData - Callback invoked for each item. Return `false` to exit early.
 * @param limit - Optional maximum number of items to process
 * @returns The number of items processed
 */
export async function readNdjson<T = any>(
  filename: string,
  onData: (item: T, index: number) => void | false,
  limit?: number | null
): Promise<number>{
  filename = fixNdjsonFilename(filename)

  const {processedItems} = await readNdJsonCallback(filename, onData, limit)
  return processedItems
}