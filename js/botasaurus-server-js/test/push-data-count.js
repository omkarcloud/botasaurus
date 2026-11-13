// The helper's db and result-file modules are replaced in the require cache, so
// no db.nedb is opened: the count updates are recorded instead of saved.
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const src = path.join(__dirname, '..', 'src');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'task-helper-count-'));
const filePath = (id) => path.join(dir, `${id}.ndjson`);

// Other test files replace these modules too, so they are put back once loaded
const replaced = {};
const stub = (file, exports) => {
  const id = require.resolve(path.join(src, file));
  replaced[id] = require.cache[id];
  require.cache[id] = { id, filename: id, loaded: true, exports };
};
stub('models', { createTask: () => {}, db: {}, Task: class {}, TaskStatus: {} });
stub('task-results', { TaskResults: { generateTaskFilePath: filePath } });
const helperId = require.resolve(path.join(src, 'task-helper'));
const loadedHelper = require.cache[helperId];
delete require.cache[helperId];
const { PushDataWriter } = require(helperId);
require.cache[helperId] = loadedHelper;
for (const [id, module] of Object.entries(replaced)) {
  if (module) require.cache[id] = module;
  else delete require.cache[id];
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Records every count saved; each save waits like a write queued behind others in db.nedb
function countSaver(ms) {
  const saved = [];
  return { saved, save: async (count) => { await sleep(ms); saved.push(count); } };
}

describe('result count updates', () => {
  it('a task pushing one item at a time saves the count every 10 items', async () => {
    const { saved, save } = countSaver(1);
    const writer = new PushDataWriter(1, null, save);
    for (let i = 0; i < 35; i++) await writer.push({ name: `place ${i}` });
    await writer.close();

    assert.deepStrictEqual(saved, [1, 11, 21, 31, 35]);
  });

  // The maps scraper pushes each place on its own from many parallel queries.
  // Every push made while a save waited saved again (task 6376: 150 places,
  // 114 saves); on a 19,909-place search the saves queued up in db.nedb and the
  // task list took 103 s (2026-11-02 week test).
  it('pushes made while a save is waiting do not save again', async () => {
    const { saved, save } = countSaver(20);
    const writer = new PushDataWriter(2, null, save);
    const pushes = [];
    for (let i = 0; i < 300; i++) {
      pushes.push(writer.push({ name: `place ${i}` }));
      if (i % 50 === 49) await sleep(5);
    }
    await Promise.all(pushes);
    await writer.close();

    assert.ok(saved.length <= 300 / 10 + 2, `${saved.length} saves for 300 items`);
    assert.strictEqual(saved[saved.length - 1], 300);
  });

  after(() => fs.rmSync(dir, { recursive: true, force: true }));
});
