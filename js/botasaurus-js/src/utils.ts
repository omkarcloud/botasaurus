import fs from 'fs'
import { relativePath } from "./decorators-utils"

class NotFoundException extends Error {
    link: string | null
    raisedOnce: boolean
    raiseMaximum1Time: boolean

    constructor(link: string | null = null, raiseMaximum1Time: boolean = true) {
        super(link ? `Not found for link: ${link}` : "Not Found")
        this.link = link
        this.raisedOnce = false
        this.raiseMaximum1Time = raiseMaximum1Time
    }
}

function isErrorsInstance(instances: any[], error: any): [boolean, number] {
    for (let i = 0; i < instances.length; i++) {
        const ins = instances[i];
        if (error instanceof ins) {
            return [true, i];
        }
    }
    return [false, -1];
}

function removeNones<A>(list: (A | null)[]): A[] {
    return list.filter((element): element is A => element !== null);
}

function writeHtml(data: string, p: string): void {
    fs.writeFileSync(p, data, { encoding: "utf-8" });
}

function writeFile(data: string, p: string): void {
    fs.writeFileSync(p, data, { encoding: "utf-8" });
}

function readJson(p: string): any {
    const data = fs.readFileSync(p, { encoding: "utf-8" });
    return JSON.parse(data);
}

function readFile(p: string): string {
    return fs.readFileSync(p, { encoding: "utf-8" });
}

function writeJson(data: any, p: string, indent: number|null = 4): void {
    fs.writeFileSync(p, JSON.stringify(data, null, indent as any), { encoding: "utf-8" });
}

function uniquifyStrings(strs: string[]): string[] {
    const seen = new Set<string>();
    return strs.filter(str => {
        if (seen.has(str)) {
            return false;
        } else {
            seen.add(str);
            return true;
        }
    });
}
export function formatExc(error: any): any {
  return error.stack || error.toString()
}

export function printExc(error: any): void {
  console.error(formatExc(error))
}

export function sleep(retryWait: number) {
  return new Promise((resolve) => setTimeout(resolve, retryWait * 1000))
}

export function isNullish(value: any): boolean {
    return value === null || value === undefined
  }

  function removeSingleSync(folderPath:string) {
    try {
      if (fs.existsSync(folderPath)) {
        const stats = fs.statSync(folderPath);
        if (stats.isDirectory()) {
          fs.rmdirSync(folderPath, { recursive: true });
        } else if (stats.isFile()) {
          fs.unlinkSync(folderPath);
        }
      }
    } catch (err) {
      console.error(err);
    }
  }  
  // Function to remove multiple folders synchronously
  function removeSync(folderPaths: string | string[]) {
    if (Array.isArray(folderPaths)) {
        folderPaths.forEach(removeSingleSync);
    } else {
        removeSingleSync(folderPaths);
    }
}
export { NotFoundException, isErrorsInstance, removeSync, removeNones, writeHtml, writeFile, readJson, readFile, writeJson, uniquifyStrings, relativePath }