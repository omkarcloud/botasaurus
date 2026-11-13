// The db, result-file and server modules are replaced in the require cache, so
// no db.nedb is opened: tasks live in an in-memory datastore and results are
// plain NDJSON files in a temp folder.
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Datastore = require('@seald-io/nedb');

const src = path.join(__dirname, '..', 'src');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'abort-task-'));
const filePath = (id) => path.join(dir, `${id}.ndjson`);
const readItems = (id) => (fs.existsSync(filePath(id)) ? fs.readFileSync(filePath(id), 'utf-8').trim().split('\n').filter(Boolean).map((line) => JSON.parse(line)) : []);
const writeItems = (id, items) => fs.writeFileSync(filePath(id), items.map((item) => JSON.stringify(item)).join('\n') + '\n');

const TaskStatus = { PENDING: 'pending', IN_PROGRESS: 'in_progress', COMPLETED: 'completed', FAILED: 'failed', ABORTED: 'aborted' };
const db = new Datastore();
// Every parent whose results were collected again
const collected = [];

// Loaded in a require cache of its own: other test files leave their stubs in
// it (task-executor.js replaces utils), and the modules loaded here with these
// stubs must not reach later files
const outer = { ...require.cache };
const clearCache = () => { for (const id of Object.keys(require.cache)) delete require.cache[id]; };
clearCache();
const stub = (file, exports) => {
  const id = require.resolve(path.join(src, file));
  require.cache[id] = { id, filename: id, loaded: true, exports };
};
stub('models', {
  createTask: () => {},
  db,
  Task: class {},
  TaskStatus,
  isFailedAndNonAllTask: (status, isAllTask) => status === TaskStatus.FAILED && !isAllTask,
});
stub('task-results', {
  TaskResults: {
    generateTaskFilePath: (id) => {
      collected.push(id);
      return filePath(id);
    },
    streamMultipleTask: async (ids, fn) => {
      let index = 0;
      for (const id of ids) {
        for (const item of readItems(id)) await fn(item, index++);
      }
    },
  },
});
stub('server', { Server: { getRemoveDuplicatesBy: () => null } });
const { performPatchTask } = require(path.join(src, 'routes-db-logic'));
clearCache();
Object.assign(require.cache, outer);

const finishedAt = new Date('2026-11-03T16:22:03Z');

async function insertSearch(parentStatus, childStatuses) {
  await db.removeAsync({}, { multi: true });
  collected.length = 0;
  await db.insertAsync({ id: 1, is_all_task: true, parent_task_id: null, scraper_name: 'google_maps_scraper', status: parentStatus, result_count: 2, finished_at: parentStatus === TaskStatus.COMPLETED ? finishedAt : null });
  for (const [i, status] of childStatuses.entries()) {
    const id = i + 2;
    await db.insertAsync({ id, is_all_task: false, parent_task_id: 1, scraper_name: 'google_maps_scraper', status, result_count: 1, finished_at: status === TaskStatus.COMPLETED ? finishedAt : null });
    writeItems(id, [{ name: `place ${id}` }]);
  }
}
const statusOf = async (id) => (await db.findOneAsync({ id })).status;

describe('aborting a task', () => {
  // The UI offers Abort on every row, finished ones too
  it('a finished search is left as it is', async () => {
    await insertSearch(TaskStatus.COMPLETED, [TaskStatus.COMPLETED, TaskStatus.COMPLETED]);
    await performPatchTask('abort', 1);
    const parent = await db.findOneAsync({ id: 1 });
    assert.strictEqual(parent.status, TaskStatus.COMPLETED);
    assert.deepStrictEqual(parent.finished_at, finishedAt);
    assert.deepStrictEqual(collected, [], 'its results were not collected again');
  });

  // Retrying a child of a completed or aborted search leaves the search's status as it was
  it('a finished search with a retried child running is still aborted', async () => {
    for (const parentStatus of [TaskStatus.COMPLETED, TaskStatus.ABORTED]) {
      await insertSearch(parentStatus, [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS]);
      await performPatchTask('abort', 1);
      assert.strictEqual(await statusOf(3), TaskStatus.ABORTED);
      assert.strictEqual(await statusOf(2), TaskStatus.COMPLETED);
      assert.strictEqual(await statusOf(1), TaskStatus.ABORTED);
    }
  });

  it('a finished child does not take its results out of its parent', async () => {
    await insertSearch(TaskStatus.IN_PROGRESS, [TaskStatus.COMPLETED, TaskStatus.COMPLETED]);
    await performPatchTask('abort', 2);
    assert.strictEqual(await statusOf(2), TaskStatus.COMPLETED);
    assert.strictEqual(await statusOf(1), TaskStatus.IN_PROGRESS);
    assert.deepStrictEqual(collected, []);
  });

  it('a running search is still aborted with the results it has', async () => {
    await insertSearch(TaskStatus.IN_PROGRESS, [TaskStatus.COMPLETED, TaskStatus.PENDING]);
    await performPatchTask('abort', 1);
    assert.strictEqual(await statusOf(1), TaskStatus.ABORTED);
    assert.strictEqual(await statusOf(3), TaskStatus.ABORTED);
    // With what the aborted child had found too
    assert.deepStrictEqual(readItems(1).map((item) => item.name).sort(), ['place 2', 'place 3']);
  });

  it('a pending child of a running search is still aborted', async () => {
    await insertSearch(TaskStatus.IN_PROGRESS, [TaskStatus.IN_PROGRESS, TaskStatus.PENDING]);
    await performPatchTask('abort', 3);
    assert.strictEqual(await statusOf(3), TaskStatus.ABORTED);
    assert.strictEqual(await statusOf(1), TaskStatus.IN_PROGRESS);
  });

  after(() => fs.rmSync(dir, { recursive: true, force: true }));
});
