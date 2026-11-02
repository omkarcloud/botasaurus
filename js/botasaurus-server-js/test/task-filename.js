const assert = require('assert');
const { taskFilename } = require('../src/paths');

describe('the filename of a task export', () => {
  it('is the name when it fits', () => {
    assert.strictEqual(taskFilename('dentist-in-reno', 7), 'dentist-in-reno');
    assert.strictEqual(taskFilename('牙医-in-北京', 7), '牙医-in-北京');
  });

  it('never is empty', () => {
    assert.strictEqual(taskFilename('', 7), 'task-7');
  });

  it('is cut short with the id, so two long names stay apart', () => {
    const a = taskFilename(`${'x'.repeat(250)}-a`, 7);
    const b = taskFilename(`${'x'.repeat(250)}-b`, 8);
    assert.notStrictEqual(a, b);
    assert.ok(Buffer.byteLength(a) <= 160);
    assert.ok(a.endsWith('-7'));
  });

  it('is not cut in the middle of a character', () => {
    const name = taskFilename('牙'.repeat(100), 7);
    assert.ok(Buffer.byteLength(name) <= 160);
    assert.ok(!name.includes('�'));
    assert.ok(name.endsWith('牙-7'));
  });
});
