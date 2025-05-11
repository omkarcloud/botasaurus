const assert = require('assert');

const {
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
  readExcel,
  writeExcel,
  readTempExcel,
  writeTempExcel,
  readTempFile,
  writeTempFile,
} = require('../src/output');

describe('JSON functions', () => {
  it('should write and read JSON file', async () => {
    const data = { name: 'John', age: 30 };
    const filename = writeJson(data, 'test.json');
    const readData = readJson(filename);
    assert.deepStrictEqual(readData, data);
  });

  it('should write and read temporary JSON file', () => {
    const data = { name: 'Alice', age: 25 };
    writeTempJson(data, false);
    const readData = readTempJson();
    assert.deepStrictEqual(readData, data);
  });
});

describe('CSV functions', () => {
  it('should write and read CSV file', () => {
    const data = [
      { name: 'John', age: '30' },
      { name: 'Alice', age: '25' },
    ];
    const filename = writeCsv(data, 'test.csv');
    const readData = readCsv(filename);
    assert.deepStrictEqual(readData, data);
  });

  it('should write and read temporary CSV file', () => {
    const data = [
      { name: 'Bob', age: '35' },
      { name: 'Eve', age: '28' },
    ];
    writeTempCsv(data, false);
    const readData = readTempCsv();
    assert.deepStrictEqual(readData, data);
  });
});

describe('HTML functions', () => {
  it('should write and read HTML file', () => {
    const data = '<html><body><h1>Hello, World!</h1></body></html>';
    const filename = writeHtml(data, 'test.html', false);
    const readData = readHtml(filename);
    assert.strictEqual(readData, data);
  });

  it('should write and read temporary HTML file', () => {
    const data = '<html><body><p>Temporary HTML</p></body></html>';
    writeTempHtml(data, false);
    const readData = readTempHtml();
    assert.strictEqual(readData, data);
  });
});

describe('File functions', () => {
  it('should write and read file', () => {
    const data = 'Hello, World!';
    const filename = writeFile(data, 'test.txt', false);
    const readData = readFile(filename);
    assert.strictEqual(readData, data);
  });

  it('should write and read temporary file', () => {
    const data = 'Temporary file content';
    writeTempFile(data, false);
    const readData = readTempFile();
    assert.strictEqual(readData, data);
  });
});

describe('Excel functions', () => {
  it('should write and read Excel file', async () => {
    const data = [
      { name: 'John', age: 30 },
      { name: 'Alice', age: 25 },
    ];
    const filename = await writeExcel(data, 'test.xlsx', false);
    const readData = await readExcel(filename);
    assert.deepStrictEqual(readData, data);
  });

  it('should write and read temporary Excel file', async () => {
    const data = [
      { name: 'Bob', age: 35 },
      { name: 'Eve', age: 28 },
    ];
    await writeTempExcel(data, false);
    const readData =  await readTempExcel();
    assert.deepStrictEqual(readData, data);
  });
});