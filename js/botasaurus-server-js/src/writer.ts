import { readFile as _readFile, writeJson as _writeJson, readJson as _readJson, writeHtml as _writeHtml, writeFile as _writeFile } from 'botasaurus/utils'
import { convertNestedToJsonInPlace,convertNestedItemToJson, getFields,convertNestedToJsonForExcelInPlace,} from 'botasaurus/output'
import { CSVWriteStream, JSONWriteStream, readNdJsonCallback } from './ndjson'
import { isNullish } from './null-utils'
import ExcelJS, {Worksheet} from 'exceljs'
import path from 'path'

function trimFilename(filename: string): string {
  filename = filename.trim()
  return filename
}

function fixJsonFilename(filename: string): string {
  filename = trimFilename(filename)

  if (!filename.endsWith('.json')) {
    filename = filename + '.json'
  }
  return filename
}

function isFileOpenError(error: any) {
  return error.code === 'EACCES'|| error.code === 'EBUSY' || error.code === 'EPERM' || (error.message && error.message.includes('EBUSY'))
}


async function applyFunctionToResult(result: any, fn: (item:any)=> any) {
  if (Array.isArray(result)) {
    for (const item of result) {
      await fn(item);
    }
  } else {
    return fn(result);
  }
}
function createCsvItemWriterFn(streamFn: any, writer: any) {
  let isPreStartCalled = false;

  return async (item:any) => {
    const result = streamFn(item)
    return applyFunctionToResult(result, async (x)=>{
      if (!isPreStartCalled) {
        await writer.preStart(Object.keys(x)); // Call preStart before reading the file
        isPreStartCalled = true;
      }
    
      await writer.push(convertNestedItemToJson(x))
    })
  }
}

function createJsonItemWriterFn(streamFn: any, writer: JSONWriteStream) {
  return async (item:any) => {
    const result = streamFn(item)
    return applyFunctionToResult(result, async (x)=>{
      await writer.push(x)
    })
  }
}

async function writeJsonStreamed(inputFileNamePath: any, filename: string, streamFn:any): Promise<string> {
  try {
    filename = trimFilename(filename)

    if (!filename.endsWith('.json')) {
      filename = filename + '.json'
    }

    const writer = new JSONWriteStream(filename)
    await writer.preStart()
    await readNdJsonCallback(inputFileNamePath, createJsonItemWriterFn(streamFn, writer))
    await writer.end()

  } catch (error: any) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filename)
      throw new Error(`${baseFilename} is currently open in another application. Please close the application and try again.`)
    }
    throw error
  }
  return filename
}


async function writeJson(data: any, filename: string): Promise<string> {
  try {
    filename = trimFilename(filename)

    if (!filename.endsWith('.json')) {
      filename = filename + '.json'
    }

    const writer = new JSONWriteStream(filename)
    await writer.preStart()
    
    for (let index = 0; index < data.length; index++) {
      const element = data[index];
      applyFunctionToResult(element, async (x)=>{
        await writer.push(x)
      })
      
    }
    await writer.end()

  } catch (error: any) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filename)
      throw new Error(`${baseFilename} is currently open in another application. Please close the application and try again.`)
    }
    throw error
  }
  return filename
}


function fixCsvFilename(filename: string): string {
  filename = trimFilename(filename)

  if (!filename.endsWith('.csv')) {
    filename = filename + '.csv'
  }
  return filename
}
async function writeCsvStreamed(inputFileNamePath: any, filename: string, streamFn:any): Promise<string> {
  let filenameNew = trimFilename(filename)

  if (!filenameNew.endsWith('.csv')) {
    filenameNew = filenameNew + '.csv'
  }

  try {

    const writer = new CSVWriteStream(filenameNew) // Use filenameNew here

    const writefn = createCsvItemWriterFn(streamFn, writer)

    await readNdJsonCallback(inputFileNamePath, async (item) => {
      return writefn(item)    
    })
    await writer.end()
  } catch (error) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filenameNew)
      throw new Error(`${baseFilename} is currently open in another application (e.g., Excel). Please close the application and try again.`)
    }
    throw error
  }
  return filenameNew
}

async function writeCsv(data: any[], filename: string): Promise<string> {
  data = convertNestedToJsonInPlace(data);

  let filenameNew = trimFilename(filename);

  if (!filenameNew.endsWith('.csv')) {
    filenameNew = filenameNew + '.csv';
  }

  try {
    const fieldnames = getFields(data);
    const writer = new CSVWriteStream(filenameNew);
    if (data.length) {
      await writer.preStart(fieldnames); // Pass fieldnames directly
    }

    for (let index = 0; index < data.length; index++) {
      const element = data[index];
      await writer.push(element)
      // release memory
      data[index] = null
    }

    await writer.end();
  } catch (error) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filenameNew)
      throw new Error(`${baseFilename} is currently open in another application (e.g., Excel). Please close the application and try again.`)
    }
    throw error;
  }
  return filenameNew;
}

function fixExcelFilename(filename: string): string {
  filename = trimFilename(filename)

  if (!filename.endsWith('.xlsx')) {
    filename = filename + '.xlsx'
  }
  return filename
}



async function writeExcel(data: any[], filename: string ): Promise<string> {
  data = convertNestedToJsonForExcelInPlace(data)

  try {
    
    filename = fixExcelFilename(filename)
    await writeWorkbook(data, filename)

  } catch (error) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filename)
      throw new Error(`${baseFilename} is currently open in another application (e.g., Excel). Please close the application and try again.`)
    }
    throw error
  }
  return filename
}

async function writeExcelStreamed(inputFileNamePath: any, filename: string, streamFn:any): Promise<string> {

  try {
    
    filename = fixExcelFilename(filename)
    await writeWorkbookStreamed(inputFileNamePath, filename, streamFn)

  } catch (error) {
    if (isFileOpenError(error)) {
      const baseFilename = path.basename(filename)
      throw new Error(`${baseFilename} is currently open in another application (e.g., Excel). Please close the application and try again.`)
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
 function makeWorksheet(worksheet: Worksheet, data: any[]) {
  if (data.length === 0) return;

  const MAX_EXCEL_LIMIT = 65530;
  let linkCount = 0;

  function createCell(value: unknown) {
    if (isNullish(value)) return null;
    if (linkCount < MAX_EXCEL_LIMIT && isUrl(value)) {
      linkCount++;
      return { text: value, hyperlink: value };
    }
    return value;
  }

  const headers = Object.keys(data[0]);
  worksheet.addRow(headers).commit();

  for (const row of data) {
    const formattedRow = Object.values(row).map(createCell);
    worksheet.addRow(formattedRow).commit();
  }
}


async function makeWorksheetStreamed(worksheet:Worksheet, inputFileNamePath: any, streamFn:any) {
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

  let isPreStartCalled = false;

  return await readNdJsonCallback(inputFileNamePath, (item) => {

    return applyFunctionToResult(streamFn(item), (x)=> {

      if (!isPreStartCalled) {
        const headers = Object.keys(x)
        worksheet.addRow(headers).commit();
        isPreStartCalled = true;
      }

      const formattedRow = Object.values(convertNestedItemToJson(x)).map(createCell)
      worksheet.addRow(formattedRow).commit() 
    })
  })
}

async function writeWorkbookBase(filename:string, exec:any) {
  const workbook = new ExcelJS.stream.xlsx.WorkbookWriter({
    filename: filename,
});
  const worksheet = workbook.addWorksheet('Sheet1');

  await exec(worksheet)
  
  await workbook.commit();

  return filename
  
}

async function writeWorkbook(data: any[], filename: string): Promise<string> {
  return writeWorkbookBase(filename, (worksheet:any) =>{
    return makeWorksheet(worksheet, data)
  })
}

async function writeWorkbookStreamed(inputFileNamePath: any, filename: string, streamFn:any): Promise<string> {
  return writeWorkbookBase(filename, (worksheet:any) =>{
    return makeWorksheetStreamed(worksheet, inputFileNamePath,streamFn )
  })
}


export {
  writeJsonStreamed,writeJson,writeCsvStreamed,
  writeCsv,
  writeExcelStreamed,writeExcel,
  fixExcelFilename, 
  fixCsvFilename, 
  fixJsonFilename,
  makeWorksheet, makeWorksheetStreamed,
}
