import { convertNestedToJsonInPlace, convertNestedItemToJson, getFields } from 'botasaurus/output';
import { readNdJsonCallback } from './ndjson';
import { HTTPJSONWriteStream, HTTPCSVWriteStream } from './ndjson-http';
import { readFile as _readFile, writeJson as _writeJson, readJson as _readJson, writeHtml as _writeHtml, writeFile as _writeFile } from 'botasaurus/utils'
import { convertNestedToJsonForExcelInPlace,} from 'botasaurus/output'
import ExcelJS from 'exceljs'
import { makeWorksheet, makeWorksheetStreamed } from './writer'
import * as fs from 'fs'
async function applyFunctionToResult(result: any, fn: (item: any) => any) {
  if (Array.isArray(result)) {
    for (const item of result) {
      await fn(item);
    }
  } else if (result != null && typeof result === 'object' && Symbol.iterator in result) {
    for (const item of result) {
      await fn(item);
    }
  } else {
    return fn(result);
  }
}

function createCsvItemWriterFn(streamFn: any, writer: any) {
  let headers: string[] | null = null;

  return (item: any) => {
    const result = streamFn(item);
    return applyFunctionToResult(result, async (x) => {
      if (!headers) {
        headers = Object.keys(x);
        writer.preStart(headers);
      }
      // By key, so a row with other keys can't put its values under the wrong headers
      const row = convertNestedItemToJson(x);
      await writer.push(headers.map((key) => row[key]));
    });
  };
}

function createJsonItemWriterFn(streamFn: any, writer: HTTPJSONWriteStream) {
  return (item: any) => {
    const result = streamFn(item);
    return applyFunctionToResult(result, async (x) => {
      await writer.push(x);
    });
  };
}

async function writeJsonStreamed(inputFilePath: any, raw: any, streamFn: any) {
  const writer = new HTTPJSONWriteStream(raw);
  writer.preStart();
  await readNdJsonCallback(inputFilePath, createJsonItemWriterFn(streamFn, writer));
  writer.end();
}

async function writeJson(data: any, raw: any) {
  const writer = new HTTPJSONWriteStream(raw);
  writer.preStart();

  for (let index = 0; index < data.length; index++) {
    const element = data[index];
    await applyFunctionToResult(element, (x) => {
      return writer.push(x);
    });
    data[index] = null; // free memory
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

async function writeCsv(data: any[], raw: any) {
  data = convertNestedToJsonInPlace(data);
  const fieldnames = getFields(data);
  const writer = new HTTPCSVWriteStream(raw);

  if (data.length) {
    writer.preStart(fieldnames);
  }

  for (let index = 0; index < data.length; index++) {
    const element = data[index];
    // By key, so a row with other keys can't put its values under the wrong headers
    await writer.push(fieldnames.map((key) => element[key]));
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

  // A workbook sent to a client that disconnected would never finish
  let failure: Error | null = null;
  const disconnected = new Promise<never>((_, reject) => rawStream.once('close', () => {
    failure = new Error('The client disconnected');
    reject(failure);
  }));

  await Promise.race([
    (async () => {
      await exec(worksheet, () => failure);
      await workbook.commit();
    })(),
    disconnected,
  ]);
}

async function writeWorkbook(data: any[], rawStream: NodeJS.WritableStream) {
  return writeWorkbookBase(rawStream, (worksheet:any) => makeWorksheet(worksheet, data));
}

async function writeWorkbookStreamed(inputFilePath: any, rawStream: NodeJS.WritableStream, streamFn: any) {
  
  return writeWorkbookBase(rawStream,(worksheet:any, getFailure:any) =>
    makeWorksheetStreamed(worksheet, inputFilePath, streamFn, getFailure)
  );
}

function writeNdjson(inputFilePath: string, rawStream: NodeJS.WritableStream): Promise<void> {
  return new Promise((resolve, reject) => {
    const readStream = fs.createReadStream(inputFilePath, { encoding: 'utf-8' });
    
    readStream.on('error', (err) => {
      reject(err);
    });
    
    readStream.on('end', () => {
      rawStream.end();
      resolve();
    });

    // pipe stops when the client disconnects, and 'end' then never comes
    rawStream.once('close', () => {
      readStream.destroy();
      resolve();
    });
    
    readStream.pipe(rawStream as any, { end: false });
  });
}

export default {
  writeJsonStreamed,writeCsvStreamed,
  writeCsv,
  writeExcelStreamed,writeExcel,
  writeJson,
  writeNdjson
}
