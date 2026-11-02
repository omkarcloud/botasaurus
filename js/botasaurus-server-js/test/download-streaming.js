const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { EventEmitter } = require('events');
const ExcelJS = require('exceljs');
const { parse } = require('csv-parse/sync');
const { writeCsvStreamed, writeExcelStreamed, writeJsonStreamed } = require('../src/writer');
const writerHttp = require('../src/writer-http').default;
const { HTTPNDJSONWriteStream } = require('../src/ndjson-http');
const { attachmentHeader } = require('../src/download');
const { NDJSONWriteStream, readNdJson, readNdJsonCallback } = require('../src/ndjson');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'download-streaming-'));
const inputFile = (rows) => {
  const file = path.join(dir, `${Math.random()}.ndjson`);
  fs.writeFileSync(file, rows.map((row) => JSON.stringify(row)).join('\n') + '\n');
  return file;
};
const identity = (item) => item;

// A rental's row has more keys; an all task's rows come from several tasks
const rows = [
  { name: 'rental', detailed_reviews: [1], query: 'q1', price: '$81' },
  { name: 'place', query: 'q2' },
  { name: 'reordered', price: '$5', query: 'q3', detailed_reviews: null },
];

// The memory of a raw response: what it was given and has not sent on
class SlowResponse extends EventEmitter {
  chunks = [];
  ended = false;
  writes = 0;
  write(chunk) {
    this.chunks.push(chunk);
    return ++this.writes % 2 !== 0;
  }
  end() { this.ended = true; }
}

describe('exports written row by row', () => {
  it('a CSV keeps every value under its own header', async () => {
    const file = await writeCsvStreamed(inputFile(rows), path.join(dir, 'a.csv'), identity);
    const out = parse(fs.readFileSync(file, 'utf-8'), { columns: true });
    assert.deepStrictEqual(out.map((row) => [row.name, row.query, row.price]), [['rental', 'q1', '$81'], ['place', 'q2', ''], ['reordered', 'q3', '$5']]);
    assert.strictEqual(out[1].detailed_reviews, '');
  });

  it('an Excel file keeps every value under its own header', async () => {
    const file = await writeExcelStreamed(inputFile(rows), path.join(dir, 'a.xlsx'), identity);
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(file);
    const sheet = workbook.getWorksheet('Sheet1');
    const headers = sheet.getRow(1).values;
    const cell = (rowNumber, header) => sheet.getRow(rowNumber).getCell(headers.indexOf(header)).value;
    assert.strictEqual(cell(3, 'query'), 'q2');
    assert.strictEqual(cell(3, 'price'), null);
    assert.strictEqual(cell(4, 'query'), 'q3');
    assert.strictEqual(cell(4, 'price'), '$5');
  });

  it('an Excel cell stays within Excel\'s limit', async () => {
    const file = await writeExcelStreamed(inputFile([{ name: 'x'.repeat(40000), reviews: [{ text: 'y'.repeat(40000) }] }]), path.join(dir, 'b.xlsx'), identity);
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(file);
    const row = workbook.getWorksheet('Sheet1').getRow(2);
    assert.strictEqual(String(row.getCell(1).value).length, 32767);
    assert.strictEqual(String(row.getCell(2).value).length, 32767);
  });

  it('an HTTP CSV keeps every value under its own header', async () => {
    const raw = new SlowResponse();
    const writing = writerHttp.writeCsvStreamed(inputFile(rows), raw, identity);
    const drain = setInterval(() => raw.emit('drain'), 1);
    await writing;
    clearInterval(drain);
    const out = parse(raw.chunks.join(''), { columns: true });
    assert.deepStrictEqual(out.map((row) => [row.name, row.query, row.price]), [['rental', 'q1', '$81'], ['place', 'q2', ''], ['reordered', 'q3', '$5']]);
    assert.strictEqual(raw.ended, true);
  });

  it('an HTTP write waits for a slow reader', async () => {
    const raw = new SlowResponse();
    const stream = new HTTPNDJSONWriteStream(raw);
    assert.strictEqual(stream.performWrite('accepted'), undefined);
    let done = false;
    const waiting = Promise.resolve(stream.performWrite('buffer full')).then(() => { done = true; });
    await new Promise((resolve) => setTimeout(resolve, 5));
    assert.strictEqual(done, false);
    raw.emit('drain');
    await waiting;
    assert.strictEqual(raw.listenerCount('drain'), 0);
    assert.strictEqual(raw.listenerCount('close'), 0);
  });

  it('an HTTP write stops waiting when the reader disconnects', async () => {
    const raw = new SlowResponse();
    const stream = new HTTPNDJSONWriteStream(raw);
    stream.performWrite('accepted');
    const waiting = stream.performWrite('buffer full');
    raw.emit('close');
    await waiting;
  });

  // Only reliable where /dev/fd lists this process's open files (macOS, Linux)
  const handlesOn = (file) => {
    if (!fs.existsSync('/dev/fd')) return 0;
    const real = fs.realpathSync(file);
    return fs.readdirSync('/dev/fd').filter((fd) => {
      try { return fs.fstatSync(Number(fd)).ino === fs.statSync(real).ino; } catch { return false; }
    }).length;
  };
  const bigFile = () => inputFile(Array.from({ length: 2000 }, (_, i) => ({ i, text: 'x'.repeat(200) })));

  it('reading part of a file leaves no file handle open', async () => {
    const file = bigFile();
    for (let i = 0; i < 5; i++) {
      assert.strictEqual((await readNdJson(file, 10)).length, 10);
      await readNdJsonCallback(file, () => {}, 10);
      await readNdJsonCallback(file, () => false);
    }
    await new Promise((resolve) => setTimeout(resolve, 20));
    assert.strictEqual(handlesOn(file), 0);
  });

  // Unreadable as a file held by security or backup software is on Windows
  const unreadableFile = () => {
    const file = inputFile(rows);
    fs.chmodSync(file, 0o000);
    return file;
  };

  it('a file that can not be read rejects instead of crashing', async () => {
    await assert.rejects(readNdJson(unreadableFile()), /EACCES/);
    await assert.rejects(readNdJsonCallback(unreadableFile(), () => {}), /EACCES/);
  });

  it('an HTTP write to a client that has gone stops the export', async () => {
    const raw = new SlowResponse();
    raw.destroyed = true;
    const stream = new HTTPNDJSONWriteStream(raw);
    assert.throws(() => stream.performWrite('x'), /disconnected/);
    await assert.rejects(writerHttp.writeCsvStreamed(inputFile(rows), raw, identity), /disconnected/);
  });

  it('an HTTP NDJSON export ends when the client disconnects', async () => {
    const { PassThrough } = require('stream');
    const raw = new PassThrough({ highWaterMark: 1 });
    const writing = writerHttp.writeNdjson(bigFile(), raw);
    setTimeout(() => raw.destroy(), 20);
    await writing;
  });

  it('an HTTP Excel export ends when the client disconnects', async () => {
    const { PassThrough } = require('stream');
    const raw = new PassThrough({ highWaterMark: 1 });
    const writing = writerHttp.writeExcelStreamed(bigFile(), raw, identity);
    setTimeout(() => raw.destroy(), 5);
    await assert.rejects(writing, /disconnected/);
  });

  it('an Excel file whose disk fills up stops reading rows', async () => {
    const { makeWorksheetStreamed } = require('../src/writer');
    let reads = 0;
    const worksheet = { addRow: () => { reads++; return { commit() {} }; } };
    const failure = new Error('no space left on device');
    await assert.rejects(makeWorksheetStreamed(worksheet, bigFile(), identity, () => (reads >= 5 ? failure : null)), /no space left/);
    assert.ok(reads <= 6, `read ${reads} rows`);
  });

  it('an attachment name in any language can be sent as a header', () => {
    assert.strictEqual(attachmentHeader('dentist-in-reno.csv'), 'attachment; filename="dentist-in-reno.csv"');
    const header = attachmentHeader('牙医-in-北京.csv');
    assert.doesNotThrow(() => new (require('http').OutgoingMessage)().setHeader('Content-Disposition', header));
    assert.ok(header.includes(encodeURIComponent('牙医-in-北京.csv')));
  });

  // A read-only file fails to open like a file locked by Excel does on Windows: an
  // 'error' event on the stream. Unhandled, that closed the whole app.
  const lockedFile = (name) => {
    const file = path.join(dir, name);
    fs.writeFileSync(file, 'old');
    fs.chmodSync(file, 0o444);
    return file;
  };

  it('a locked CSV says the file is open instead of crashing', async () => {
    await assert.rejects(writeCsvStreamed(inputFile(rows), lockedFile('locked.csv'), identity), /locked\.csv is currently open in another application/);
  });

  it('a locked JSON says the file is open instead of crashing', async () => {
    await assert.rejects(writeJsonStreamed(inputFile(rows), lockedFile('locked.json'), identity), /locked\.json is currently open in another application/);
  });

  it('a locked Excel file says the file is open instead of crashing', async () => {
    await assert.rejects(writeExcelStreamed(inputFile(rows), lockedFile('locked.xlsx'), identity), /locked\.xlsx is currently open in another application/);
  });

  it('a write that fails rejects, also one waiting for the buffer to empty', async () => {
    const file = path.join(dir, 'fails.ndjson');
    const stream = new NDJSONWriteStream(file);
    await stream.push({ a: 1 });
    const big = stream.performWrite('x'.repeat(1024 * 1024));
    stream.writeStream.emit('error', Object.assign(new Error('no space left on device'), { code: 'ENOSPC' }));
    await assert.rejects(big, /no space left/);
    await assert.rejects(stream.push({ a: 2 }), /no space left/);
    await assert.rejects(stream.end(), /no space left/);
  });

  it('a stream that fails with nothing waiting does not throw', async () => {
    const stream = new NDJSONWriteStream(lockedFile('nothing-waiting.ndjson'));
    await new Promise((resolve) => setTimeout(resolve, 20));
    await assert.rejects(stream.end(), /EACCES/);
  });

  it('a normal stream still writes everything', async () => {
    const file = path.join(dir, 'ok.ndjson');
    const stream = new NDJSONWriteStream(file);
    for (let i = 0; i < 2000; i++) await stream.push({ i, text: 'x'.repeat(200) });
    await stream.end();
    assert.strictEqual(fs.readFileSync(file, 'utf-8').trim().split('\n').length, 2000);
  });

  after(() => fs.rmSync(dir, { recursive: true, force: true }));
});
