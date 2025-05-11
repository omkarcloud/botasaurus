import { convertNestedToJsonInPlace, convertNestedItemToJson, getFields } from 'botasaurus/output';
import { readNdJsonCallback } from './ndjson';
import { HTTPJSONWriteStream, HTTPCSVWriteStream } from './ndjson-http';
import { readFile as _readFile, writeJson as _writeJson, readJson as _readJson, writeHtml as _writeHtml, writeFile as _writeFile } from 'botasaurus/utils'
import { convertNestedToJsonForExcelInPlace,} from 'botasaurus/output'
import ExcelJS from 'exceljs'
import { makeWorksheet, makeWorksheetStreamed } from './writer'
function applyFunctionToResultSync(result: any, fn: (item: any) => any) {
  if (Array.isArray(result)) {
    for (const item of result) {
      fn(item);
    }
  } else {
    return fn(result);
  }
}

function createCsvItemWriterFn(streamFn: any, writer: any) {
  let isPreStartCalled = false;

  return (item: any) => {
    const result = streamFn(item);
    return applyFunctionToResultSync(result, (x) => {
      if (!isPreStartCalled) {
        writer.preStart(Object.keys(x));
        isPreStartCalled = true;
      }
      writer.push(convertNestedItemToJson(x));
    });
  };
}

function createJsonItemWriterFn(streamFn: any, writer: HTTPJSONWriteStream) {
  return (item: any) => {
    const result = streamFn(item);
    return applyFunctionToResultSync(result, (x) => {
      writer.push(x);
    });
  };
}

async function writeJsonStreamed(inputFilePath: any, raw: any, streamFn: any) {
  const writer = new HTTPJSONWriteStream(raw);
  writer.preStart();
  await readNdJsonCallback(inputFilePath, createJsonItemWriterFn(streamFn, writer));
  writer.end();
}

function writeJson(data: any, raw: any) {
  const writer = new HTTPJSONWriteStream(raw);
  writer.preStart();

  for (let index = 0; index < data.length; index++) {
    const element = data[index];
    applyFunctionToResultSync(element, (x) => {
      return writer.push(x);
    });
  }
  writer.end();
}

async function writeCsvStreamed(inputFilePath: any, raw: any, streamFn: any) {
  const writer = new HTTPCSVWriteStream(raw);
  const writefn = createCsvItemWriterFn(streamFn, writer);

  await readNdJsonCallback(inputFilePath, (item) => {
    return writefn(item);
  });

  writer.end();
}

function writeCsv(data: any[], raw: any) {
  data = convertNestedToJsonInPlace(data);
  const fieldnames = getFields(data);
  const writer = new HTTPCSVWriteStream(raw);

  if (data.length) {
    writer.preStart(fieldnames);
  }

  for (let index = 0; index < data.length; index++) {
    const element = data[index];
    writer.push(element);
    data[index] = null; // free memory
  }

  writer.end();
}

async function writeExcel(data: any[], rawStream: NodeJS.WritableStream) {
  data = convertNestedToJsonForExcelInPlace(data);
  await writeWorkbook(data, rawStream);
}

async function writeExcelStreamed(inputFilePath: any, rawStream: NodeJS.WritableStream, streamFn: any) {
  await writeWorkbookStreamed(inputFilePath, rawStream, streamFn);
}

async function writeWorkbookBase(rawStream: NodeJS.WritableStream, exec:any) {
  const workbook = new ExcelJS.stream.xlsx.WorkbookWriter({
    stream: rawStream as any,
  });
  const worksheet = workbook.addWorksheet('Sheet1');

  await exec(worksheet);

  await workbook.commit();
}

async function writeWorkbook(data: any[], rawStream: NodeJS.WritableStream) {
  return writeWorkbookBase(rawStream, (worksheet:any) => makeWorksheet(worksheet, data));
}

async function writeWorkbookStreamed(inputFilePath: any, rawStream: NodeJS.WritableStream, streamFn: any) {
  
  return writeWorkbookBase(rawStream,(worksheet:any) =>
    makeWorksheetStreamed(worksheet, inputFilePath, streamFn)
  );
}
export default {
  writeJsonStreamed,writeCsvStreamed,
  writeCsv,
  writeExcelStreamed,writeExcel,
  writeJson
}
