import fs from 'fs';
import path from 'path';

import { IS_VM_OR_DOCKER, IS_PRODUCTION as _IS_PRODUCTION } from './env';
import { isNullish, removeSync, writeFile } from './utils';
import { writeExcel, writeJson, writeCsv, fixExcelFilename, fixCsvFilename, fixJsonFilename } from './output';
import { createDirectoryIfNotExists, relativePath } from './decorators-utils';
import { Formats } from './formats';

class RetryException extends Error {}

const IS_PRODUCTION = IS_VM_OR_DOCKER || _IS_PRODUCTION;

let firstRun = false;
function printRunning() {
  if (!firstRun) {
    firstRun = true;
    console.log('Running');
  }
}

function printFilenames(writtenFilenames: string[]) {
  if (writtenFilenames.length > 0) {
    console.log('Written');
    for (const filename of writtenFilenames) {
      console.log('    ', filename);
    }
  }
}

function writeOutput(
  output: string | ((data: any, result: any) => void) | null,
  outputFormats: string[] | null,
  data: any,
  result: any,
  fnName: string
) {
  const writtenFilenames: string[] = [];

  if (isNullish(output)) {
    return result;
  }
  if (typeof output === 'function') {
    output(data, result);
  } else {
    outputFormats = outputFormats || [Formats.JSON];

    const defaultFilename = output === 'default' ? fnName : output;

    for (const fm of outputFormats) {
      if (fm === Formats.JSON) {
        // @ts-ignore
        const filename = fixJsonFilename(defaultFilename);
        writtenFilenames.push(filename);
        writeJson(result, filename, false);
      } else if (fm === Formats.CSV) {
        // @ts-ignore
        const filename = fixCsvFilename(defaultFilename);
        writtenFilenames.push(filename);
        writeCsv(result, filename, false);
      } else if (fm === Formats.EXCEL) {
        // @ts-ignore
        const filename = fixExcelFilename(defaultFilename);
        writtenFilenames.push(filename);
        writeExcel(result, filename, false);
      }
    }
  }

  printFilenames(writtenFilenames);
}

function cleanErrorLogs(errorLogsDir: string, sortKey: (folder: string) => Date) {
  const folders = fs.readdirSync(errorLogsDir);

  const sortedFolders = folders.sort((a, b) => sortKey(b).getTime() - sortKey(a).getTime());

  const foldersToDelete = sortedFolders.slice(10);
  const folderPaths = foldersToDelete.map(folder => path.join(errorLogsDir, folder));

  removeSync(folderPaths);  
}
const pad = (num:any) => num.toString().padStart(2, '0');

function convertStringToDate(dateString:any) {
  // Split the string into date and time parts
  const [datePart, timePart] = dateString.split('_');
  
  // Split date and time into components
  const [year, month, day] = datePart.split('-');
  const [hours, minutes, seconds] = timePart.split('-');
  
  // Create a new Date object
  // Note: months are 0-indexed in JavaScript Date objects
  return new Date(year, month - 1, day, hours, minutes, seconds);
}
function getCurrentFormattedDate() {
  const now = new Date();
  
  
  const year = now.getFullYear();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  
  return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

function saveErrorLogs(exceptionLog: string, driver: any) {
  const mainErrorDirectory = relativePath('error_logs');
  createDirectoryIfNotExists(mainErrorDirectory );

  const timestamp = getCurrentFormattedDate();
  const errorDirectory = relativePath(`${mainErrorDirectory}/${timestamp}`);
  createDirectoryIfNotExists(errorDirectory );

  const errorFilename = relativePath(`${errorDirectory}/error.log`);
  // const screenshotFilename = `${errorDirectory}/screenshot.png`;
  // const pageFilename = `${errorDirectory}/page.html`;

  writeFile(exceptionLog, errorFilename);

  if (driver !== null) {
    // TODO
  }

  cleanErrorLogs(relativePath('error_logs'), convertStringToDate);
}

function evaluateProxy(proxy: string | string[]) {
  if (Array.isArray(proxy)) {
    return proxy[Math.floor(Math.random() * proxy.length)];
  }
  return proxy;
}

export {
    RetryException,
    IS_PRODUCTION,
    printRunning,
    printFilenames,
    writeOutput,
    cleanErrorLogs,
    saveErrorLogs,
    evaluateProxy
};