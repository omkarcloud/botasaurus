import * as fs from 'fs';
import readline from 'readline'
import { _readJsonFiles, _has,_remove, _deleteItems, _hash } from 'botasaurus/cache';
import { appendOutputIfNeeded } from 'botasaurus/output';
import { isNotNullish } from './null-utils'
import { stringify } from 'csv-stringify/sync'

export class NDJSONWriteStream {
  private writeStream: fs.WriteStream;

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
  }

  async push(data: any): Promise<void> {
    return this.performWrite(JSON.stringify(data) + '\n');
  }

   performWrite(content: any): void | PromiseLike<void> {
    return new Promise((resolve) => {
      if (!this.writeStream.write(content)) {
        this.writeStream.once('drain', () => {
          resolve() // Resolve the promise if write is successful
        })
      } else {
        resolve() // Resolve the promise if write is successful
      }
    })
  }

  end(): Promise<void> {
    return new Promise(async (resolve) => {
      await this.preEnd()
      this.writeStream.end(() => {
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
  
    return new Promise((resolve) => {
      rl.on('close', () => {
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