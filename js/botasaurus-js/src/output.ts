import * as fs from 'fs';
import { createOutputDirectoryIfNotExists } from './decorators-utils'
import { readFile as _readFile, relativePath, writeJson as _writeJson, readJson as _readJson, writeHtml as _writeHtml, writeFile as _writeFile, isNullish } from './utils'
import { prompt } from './beep-utils'
import { parse } from 'csv-parse/sync'
import axios from 'axios'
import { stringify } from 'csv-stringify/sync'
import ExcelJS, {Worksheet} from 'exceljs'

function isSlashNotInFilename(filename: string): boolean {
  return !filename.includes('/') && !filename.includes('\\')
}

function appendOutputIfNeeded(filename: string): string {
  
  filename = filename.trim()
  if (isSlashNotInFilename(filename)) {
    createOutputDirectoryIfNotExists()
    return 'output/' + filename
  }
  return filename
}

function fixJsonFilename(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.json')) {
    filename = filename + '.json'
  }
  return filename
}

function readJson(filename: string): any {
  filename = fixJsonFilename(filename)

  return _readJson(filename)
}

function isFileOpenError(error: any) {
  return error.code === 'EACCES' || error.code === 'EPERM' || (error.message && error.message.includes('EBUSY'))
}

function writeTempJson(data: any, log: boolean = true): string {
  let filename = 'temp'

  try {
    filename = appendOutputIfNeeded(filename)

    if (!filename.endsWith('.json')) {
      filename = filename + '.json'
    }

    _writeJson(data, filename)

    if (log) {
      console.log(`View written JSON file at ${filename}`)
    }
  } catch (error: any) {
    if (isFileOpenError(error)) {
      prompt(`${filename} is currently open in another application. Please close the application and press 'Enter' to save.`)
      return writeTempJson(data, log)
    }
    throw error
  }

  return filename
}

function readTempJson(): any {
  const filename = fixJsonFilename('temp')
  return _readJson(filename)
}


function writeJson(data: any, filename: string, log: boolean = true): string {
  try {
    filename = appendOutputIfNeeded(filename)

    if (!filename.endsWith('.json')) {
      filename = filename + '.json'
    }

    _writeJson(data, filename)

    if (log) {
      console.log(`View written JSON file at ${filename}`)
    }
  } catch (error: any) {
    if (isFileOpenError(error)) {
      prompt(`${filename} is currently open in another application. Please close the application and press 'Enter' to save.`)
      return writeJson(data, filename, log)
    }
    throw error
  }
  return filename
}

function writeTempCsv(data: any[], log: boolean = true): string {
  return writeCsv(data, 'temp.csv', log)
}

function readTempCsv(): any[] {
  return readCsv('temp.csv')
}

function fixCsvFilename(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.csv')) {
    filename = filename + '.csv'
  }
  return filename
}

function readCsv(filename: string): any[] {
  filename = fixCsvFilename(filename)

  const fileContent = readFile(filename)
  const records = parse(fileContent, {
    columns: true, // Treat the first line as header
    skip_empty_lines: true,
  })

  return records
}

function getFieldnames(dataList: any[]): string[] {
  const fieldnamesDict: { [key: string]: any } = {}
  for (const item of dataList) {
    for (const key of Object.keys(item)) {
      if (!(key in fieldnamesDict)) {
        fieldnamesDict[key] = null
      }
    }
  }
  return Object.keys(fieldnamesDict)
}


function convertNestedToJson(inputList: any[]): any[] {
  return inputList.map(convertNestedItemToJson);
}

function convertNestedToJsonInPlace(inputList: any[]): any[] {
  for (let i = 0; i < inputList.length; i++) {
    inputList[i] = convertNestedItemToJson(inputList[i]);
  }

  return inputList;
}
function convertNestedItemToJson(item: any) {
  const processedDict: { [key: string]: any}  = {}
  for (const [key, value] of Object.entries(item)) {
    if (typeof value === 'object' && !isNullish(value)) {
      processedDict[key] = JSON.stringify(value)
    } else {
      processedDict[key] = value
    }
  }
  return processedDict
}

function cap(str: string): string {
  if (str.length > 32767) {
    return str.substring(0, 32767 - 3) + '...'
  }
  return str
}

function convertNestedItemToJsonForExcel(item: any) {
  const processedDict: { [key: string]: any}  = {}
  for (const [key, value] of Object.entries(item)) {
    if (typeof value === 'object' && !isNullish(value)) {
      processedDict[key] = cap(JSON.stringify(value))
    } else if (typeof value === 'string') {
      processedDict[key] = cap(value)
    } else {
      processedDict[key] = value
    }
  }
  return processedDict
}
function convertNestedToJsonForExcel(inputList: any[]): any[] {
  return inputList.map(convertNestedItemToJsonForExcel);
}

function convertNestedToJsonForExcelInPlace(inputList: any[]): any[] {
  for (let i = 0; i < inputList.length; i++) {
    inputList[i] = convertNestedItemToJsonForExcel(inputList[i]);
  }

  return inputList;
}


function removeNonObjects(data: any[]): any[] {
  return data.filter((x) => typeof x === 'object' && (x !== null || x !== undefined))
}


function writeCsv(data: any[], filename: string, log: boolean = true): string {
  data = cleanData(data)
  data = convertNestedToJson(data)

  let filenameNew = appendOutputIfNeeded(filename)

  if (!filenameNew.endsWith('.csv')) {
    filenameNew = filenameNew + '.csv'
  }

  try {
    const fieldnames = getFields(data)
    const output = stringify(data, { header: true, columns: fieldnames })
    _writeFile(output, filenameNew,)

    if (log) {
      console.log(`View written CSV file at ${filenameNew}`)
    }
  } catch (error) {
    if (isFileOpenError(error)) {
      prompt(`${filenameNew} is currently open in another application (e.g., Excel). Please close the application and press 'Enter' to save.`)
      return writeCsv(data, filename, log)
    }
    throw error
  }
  return filenameNew
}

async function saveImage(url: string, filename?: string): Promise<string> {
  if (!filename) {
    filename = url.split('/').pop() || ''
  }
  try {
    const response = await axios.get(url, { responseType: 'arraybuffer' })
    if (response.status === 200) {
      const path = appendOutputIfNeeded(filename)
      fs.writeFileSync(relativePath(path), response.data)
      return path
    } else {
      console.log('Failed to download the image.')
      return ''
    }
  } catch (error) {
    console.log('Failed to download the image.')
    return ''
  }
}

function writeHtml(data: string, filename: string, log: boolean = true): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.html')) {
    filename = filename + '.html'
  }

  _writeHtml(data, filename)
  if (log) {
    console.log(`View written HTML file at ${filename}`)
  }
  return filename
}

function readHtml(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.html')) {
    filename = filename + '.html'
  }

  return _readFile(filename)
}

function writeTempHtml(data: string, log: boolean = true): string {
  return writeHtml(data, 'temp.html', log)
}

function readTempHtml(): string {
  return readHtml('temp.html')
}

function writeFile(data: string, filename: string, log: boolean = true): string {
  filename = appendOutputIfNeeded(filename)

  _writeFile(data, filename)
  if (log) {
    console.log(`View written file at ${filename}`)
  }

  return filename
}

function readFile(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  return _readFile(filename)
}

function writeTempFile(data: string, log: boolean = true): string {
  return writeFile(data, 'temp.txt', log)
}

function readTempFile(): string {
  return readFile('temp.txt')
}
function normalizeData(data: any): any[] {
  if (data === null || data === undefined) {
    return []
  } else if (Array.isArray(data)) {
    const normalizedList: any[] = []
    for (const item of data) {
      if (item === null || item === undefined) {
        continue
      } else if (typeof item !== 'object') {
        normalizedList.push({ data: item })
      } else {
        normalizedList.push(item)
      }
    }
    return normalizedList
  } else if (typeof data === 'object') {
    return [data]
  } else {
    return [{ data }]
  }
}

function normalizeItem(fieldnames: string[], item: any) {
  const filteredItem: { [key: string]: any}  = {}
  for (const key of fieldnames) {
    filteredItem[key] = item[key] === undefined ? null : item[key]
  }
  return filteredItem
}

function normalizeDictsByFieldnames(data: any[]): any[] {
  const fieldnames = getFieldnames(data);
  return data.map(item => normalizeItem(fieldnames, item));
}

function normalizeDictsByFieldnamesInPlace(data: any[]): any[] {
  const fieldnames = getFieldnames(data);

  for (let i = 0; i < data.length; i++) {
    data[i] = normalizeItem(fieldnames, data[i]);
  }

  return data;
}
function cleanData(data: any): any[] {
  return normalizeDictsByFieldnames(normalizeData(data))
}

function cleanDataInPlace(data: any): any[] {
  return normalizeDictsByFieldnamesInPlace(normalizeData(data))
}

function fixExcelFilename(filename: string): string {
  filename = appendOutputIfNeeded(filename)

  if (!filename.endsWith('.xlsx')) {
    filename = filename + '.xlsx'
  }
  return filename
}
  
async function writeExcel(data: any[], filename: string, log: boolean = true): Promise<string> {
  data = cleanData(data)
  data = convertNestedToJsonForExcel(data)

  try {
    filename = fixExcelFilename(filename)
    await writeWorkbook(data, filename)

    if (log) {
      console.log(`View written Excel file at ${filename}`)
    }
  } catch (error) {
    if (isFileOpenError(error)) {
      prompt(`${filename} is currently open in another application (e.g., Excel). Please close the application and press 'Enter' to save.`)
      return writeExcel(data, filename, log)
    }
    throw error
  }
  return filename
}

function isValidLink(value:string) {
  try {
    new URL(value);
    return true;
  } catch (error) {
    return false;
  }
}
function isUrl(value:any) {
  return (
    typeof value === 'string' &&
    (value.startsWith('http://') || value.startsWith('https://')) && isValidLink(value)
  )
}

function makeWorksheet(worksheet:Worksheet, data: any[]) {
  if (data.length === 0) {
    return
  } else {
    const MAX_EXCEL_LIMIT = 65530
    let linkCount = 0;
    function createCell(value: unknown) {
      if (isNullish(value)) {
        return null
      } else {
        let cell: any = value
        
        if (linkCount < MAX_EXCEL_LIMIT && isUrl(value)) {
          cell = {
            text: value,
            hyperlink: value,
          }
          linkCount++;
        }
        return cell
      }
    }
    
    const headers = Object.keys(data[0])
    worksheet.addRow(headers).commit();
    
    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      const formattedRow = Object.values(row).map(createCell)
      worksheet.addRow(formattedRow).commit() 
    }
  }
}

async function writeWorkbookBase(filename:string, exec:(x:any)=>void) {
  const workbook = new ExcelJS.stream.xlsx.WorkbookWriter({
    filename: filename,
});
  const worksheet = workbook.addWorksheet('Sheet1');

  exec(worksheet)
  
  await workbook.commit();

  return filename
}

async function writeWorkbook(data: any[], filename: string){
  return writeWorkbookBase(filename, (worksheet:any) =>{
    return makeWorksheet(worksheet, data)
  })
}

function getFields(data: any[]): string[] {
  if (data.length === 0) {
    return []
  }
  return Object.keys(data[0])
}

async function readExcelFile(filePath:string) {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  const data:any[] = [];

  workbook.eachSheet((sheet) => {
      const headers:string[] = [];
      sheet.eachRow((row, rowNumber) => {
          // Assume first row is headers
          if (rowNumber === 1) {
              row.eachCell((cell) => {
                  headers.push(cell.value as any);
              });
          } else {
              const rowData = {};
              row.eachCell((cell, colNumber) => {
                  const header = typeof headers[colNumber - 1] === 'string' ? headers[colNumber - 1] : `Column${colNumber}`;
                  let value = cell.value;
                  // if value contains keys text and hyperlink then value becomes hyperlink
                  // @ts-ignore
                  if (value && typeof value === 'object' && value.text && value.hyperlink) {
                    // @ts-ignore
                    value = value.hyperlink ;
                  }
                  // @ts-ignore
                  rowData[header] = value;
              });
              data.push(rowData);
          }
      });
  });
  return data;
}
async function readExcel(filename: string): Promise<any[]> {
  filename = fixExcelFilename(filename)

  const data = await readExcelFile(filename)

  return data
}

function writeTempExcel(data: any[], log: boolean = true) {
  return writeExcel(data, 'temp.xlsx', log)
}

function readTempExcel() {
  return readExcel('temp.xlsx')
}

export {
  removeNonObjects,
  readJson,
  writeJson,
  readTempJson,
  writeTempJson,
  readCsv,
  writeCsv,
  readTempCsv,
  writeTempCsv,
  readHtml,
  writeHtml,
  readTempHtml,
  writeTempHtml,
  readFile,
  writeFile,
  saveImage,
  readExcel,
  writeExcel,
  readTempExcel,
  writeTempExcel,
  readTempFile,
  writeTempFile,
  getFieldnames,
  normalizeData,
  normalizeDictsByFieldnames,
  cleanData,
  fixExcelFilename, fixCsvFilename, fixJsonFilename,
  convertNestedToJson,convertNestedItemToJson, getFields, convertNestedToJsonForExcel,
  normalizeDictsByFieldnamesInPlace,
convertNestedToJsonForExcelInPlace,
convertNestedToJsonInPlace,
cleanDataInPlace, 
normalizeItem, 
}

// zipFiles,
// uploadToS3,
// downloadFromS3,
