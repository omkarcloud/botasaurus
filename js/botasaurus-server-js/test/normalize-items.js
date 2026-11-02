// The helper's db and result-file modules are replaced in the require cache, so
// no db.nedb is opened: tasks' results are plain NDJSON files in a temp folder.
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const src = path.join(__dirname, '..', 'src');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'task-helper-keys-'));
const filePath = (id) => path.join(dir, `${id}.ndjson`);
const readItems = (id) => fs.readFileSync(filePath(id), 'utf-8').trim().split('\n').map((line) => JSON.parse(line));
const writeItems = (id, items) => fs.writeFileSync(filePath(id), items.map((item) => JSON.stringify(item)).join('\n') + '\n');

// Other test files replace these modules too, so they are put back once loaded
const replaced = {};
const stub = (file, exports) => {
  const id = require.resolve(path.join(src, file));
  replaced[id] = require.cache[id];
  require.cache[id] = { id, filename: id, loaded: true, exports };
};
stub('models', { createTask: () => {}, db: {}, Task: class {}, TaskStatus: {} });
stub('task-results', {
  TaskResults: {
    generateTaskFilePath: filePath,
    streamMultipleTask: async (ids, fn) => {
      let index = 0;
      for (const id of ids) {
        for (const item of readItems(id)) await fn(item, index++);
      }
    },
  },
});
const helperId = require.resolve(path.join(src, 'task-helper'));
const loadedHelper = require.cache[helperId];
delete require.cache[helperId];
const { PushDataWriter, normalizeAndDeduplicateChildrenTasks } = require(helperId);
require.cache[helperId] = loadedHelper;
for (const [id, module] of Object.entries(replaced)) {
  if (module) require.cache[id] = module;
  else delete require.cache[id];
}

const place = (name) => ({ name, query: 'q' });
const rental = (name) => ({ name, detailed_reviews: [], query: 'q', price: '$81' });
const keysOf = (items) => [...new Set(items.map((item) => Object.keys(item).join()))];

describe('items with different keys', () => {
  it('a parent is normalized when the first item has every key', async () => {
    writeItems(1, [rental('a'), place('b')]);
    writeItems(2, [place('c')]);
    await normalizeAndDeduplicateChildrenTasks([1, 2], 3, null);

    const items = readItems(3);
    assert.deepStrictEqual(keysOf(items), ['name,detailed_reviews,query,price']);
    assert.strictEqual(items[2].query, 'q');
    assert.strictEqual(items[2].price, null);
  });

  it('a parent is normalized when its tasks have the same keys in another order', async () => {
    writeItems(4, [{ name: 'a', query: 'q', price: 1 }]);
    writeItems(5, [{ name: 'b', price: 2, query: 'q' }]);
    await normalizeAndDeduplicateChildrenTasks([4, 5], 6, null);

    assert.deepStrictEqual(keysOf(readItems(6)), ['name,query,price']);
  });

  it('a parent whose items all match keeps them as they are', async () => {
    writeItems(7, [place('a')]);
    writeItems(8, [place('b')]);
    await normalizeAndDeduplicateChildrenTasks([7, 8], 9, null);

    assert.deepStrictEqual(readItems(9), [place('a'), place('b')]);
  });

  it('a task is normalized when its first item has every key', async () => {
    const writer = new PushDataWriter(10, null);
    await writer.push([rental('a'), place('b')]);
    await writer.close();

    assert.deepStrictEqual(keysOf(readItems(10)), ['name,detailed_reviews,query,price']);
  });

  it('a task is normalized when a later item adds keys', async () => {
    const writer = new PushDataWriter(11, null);
    await writer.push([place('a'), rental('b')]);
    await writer.close();

    assert.deepStrictEqual(keysOf(readItems(11)), ['name,query,detailed_reviews,price']);
  });

  after(() => fs.rmSync(dir, { recursive: true, force: true }));
});
