// The task executor's own modules are replaced in the require cache, so no
// db.nedb is opened: the tasks live in an in-memory nedb whose writes can be
// made to fail the way a locked or full datafile fails (nedb has already
// changed the docs in memory when the append throws).
const assert = require('assert');
const path = require('path');
const Datastore = require('@seald-io/nedb');

const src = path.join(__dirname, '..', 'src');
const TaskStatus = { PENDING: 'pending', IN_PROGRESS: 'in_progress', COMPLETED: 'completed', FAILED: 'failed', ABORTED: 'aborted' };

const db = new Datastore({ timestampData: true });
let failWrites = false;
const persistNewStateAsync = db.persistence.persistNewStateAsync.bind(db.persistence);
db.persistence.persistNewStateAsync = async (docs) => {
  if (failWrites) {
    throw Object.assign(new Error("EBUSY: resource busy or locked, open 'db.nedb'"), { code: 'EBUSY' });
  }
  return persistNewStateAsync(docs);
};

let scrape = async () => [];
let closeFails = false;
let pushDataUsed = false;
const cached = [];
const saved = [];
const deleted = [];
let cachingTaskId = null;

class PushDataWriter {
  wasUsed() { return pushDataUsed; }
  async push() {}
  async close() {
    if (closeFails) throw new Error('EBUSY while saving the result count');
  }
  getFilePath() { return 'results.ndjson'; }
  getItemCount() { return 1; }
}

const updateTask = async (id, data, inStatus) => {
  const query = inStatus ? { id, status: { $in: inStatus } } : { id };
  const { numAffected } = await db.updateAsync(query, { $set: data });
  return numAffected;
};

function stub(request, exports) {
  const filename = require.resolve(request, { paths: [src] });
  require.cache[filename] = { id: filename, filename, loaded: true, exports };
}

stub(path.join(src, 'models'), { db, TaskStatus, serializeTaskForRunTask: (t) => t, removeDuplicatesByKey: (x) => x });
stub(path.join(src, 'server'), {
  Server: {
    isScraperBasedRateLimit: true,
    cache: true,
    validateRateLimit: () => {},
    getRateLimit: () => ({ scraper: 1 }),
    getScrapersNames: () => ['scraper'],
    getScrapingFunction: () => (data, options) => scrape(data, options),
    getRemoveDuplicatesBy: () => null,
    getOnComplete: () => null,
  },
  getScraperErrorMessage: () => 'unknown scraper',
});
stub(path.join(src, 'task-helper'), {
  PushDataWriter,
  TaskHelper: {
    updateTask,
    isTaskAborted: async (id) => (await db.findOneAsync({ id }))?.status === TaskStatus.ABORTED,
  },
});
stub(path.join(src, 'task-results'), {
  TaskResults: {
    saveTask: async (id, result) => { saved.push({ id, result }); return 'results.ndjson'; },
    saveCachedTask: async () => { cached.push(cachingTaskId); },
    copyTaskToCachedTask: async () => { cached.push(cachingTaskId); },
    deleteTask: (id) => { deleted.push(id); },
  },
});
stub(path.join(src, 'utils'), { isNotEmptyObject: (o) => !!o && Object.keys(o).length > 0, omitKeys: (o) => o, isLargeFile: () => false });
stub(path.join(src, 'ndjson'), { readNdJsonCallback: async () => {} });
stub('botasaurus/dontcache', { isDontCache: () => false });
stub('botasaurus/utils', { formatExc: (e) => String(e) });
stub('botasaurus/output', { cleanDataInPlace: (x) => x });

const { TaskExecutor } = require(path.join(src, 'task-executor'));

let nextId = 1;
async function addTask(status = TaskStatus.PENDING) {
  const id = nextId++;
  await db.insertAsync({ id, status, scraper_name: 'scraper', scraper_type: 'task', is_all_task: false, priority: 0, sort_id: id, parent_task_id: null, data: {}, started_at: null, finished_at: null, result_count: 0 });
  return id;
}
const statusOf = async (id) => (await db.findOneAsync({ id })).status;

function newExecutor() {
  const executor = new TaskExecutor();
  executor.load();
  return executor;
}

// Runs one task to the end the way the worker does, holding its slot
async function run(executor, id) {
  await updateTask(id, { status: TaskStatus.IN_PROGRESS });
  executor.incrementCapacity('scraper');
  cachingTaskId = id;
  await executor.runTask(await db.findOneAsync({ id }));
}

function silenceConsoleError() {
  const original = console.error;
  console.error = () => {};
  return () => { console.error = original; };
}

describe('TaskExecutor', () => {
  it('keeps the worker loop running after a pick fails to save, and retries the picked task', async () => {
    const id = await addTask();
    const executor = newExecutor();
    const scheduled = [];
    const originalSetTimeout = global.setTimeout;
    global.setTimeout = (_fn, ms) => { scheduled.push(ms); return 0; };
    const restoreConsole = silenceConsoleError();
    failWrites = true;
    try {
      // This used to reject without scheduling the next tick, leaving every task pending
      await executor.taskWorkerScraperBased();
    } finally {
      failWrites = false;
      global.setTimeout = originalSetTimeout;
      restoreConsole();
    }
    assert.deepStrictEqual(scheduled, [1000]);
    assert.strictEqual(await statusOf(id), TaskStatus.PENDING, 'the failed pick is put back to pending');
    assert.strictEqual(executor.getCurrentRunningCount('scraper'), 0, 'no slot is taken by a task that never started');

    // Once the datafile can be written again, the next pick starts it
    let started = false;
    scrape = async () => { started = true; return []; };
    await executor.processScraperBasedTasks();
    await new Promise((resolve) => setTimeout(resolve, 50));
    assert.ok(started);
    assert.strictEqual(await statusOf(id), TaskStatus.COMPLETED);
    assert.strictEqual(executor.getCurrentRunningCount('scraper'), 0);
  });

  it('reports a failed task as failed even when closing its results throws', async () => {
    const id = await addTask();
    const executor = newExecutor();
    scrape = async () => { throw new Error('scraper crashed'); };
    closeFails = true;
    const restoreConsole = silenceConsoleError();
    try {
      await run(executor, id);
    } finally {
      closeFails = false;
      restoreConsole();
    }
    // This used to skip the report, so the task stayed "in progress" forever
    assert.strictEqual(await statusOf(id), TaskStatus.FAILED);
    assert.strictEqual(executor.getCurrentRunningCount('scraper'), 0);
  });

  it('keeps the results of a finished task when saving its completion fails', async () => {
    const id = await addTask();
    const executor = newExecutor();
    const result = [{ place_id: 'c' }];
    // The datafile becomes unwritable just as the scraper finishes: nedb marks
    // the task completed in memory, then the write of that throws
    scrape = async () => { failWrites = true; return result; };
    const restoreConsole = silenceConsoleError();
    saved.length = 0;
    deleted.length = 0;
    try {
      await run(executor, id);
    } finally {
      failWrites = false;
      restoreConsole();
    }
    assert.strictEqual(await statusOf(id), TaskStatus.COMPLETED);
    // This used to replace the results with the error and then delete them
    assert.deepStrictEqual(saved, [{ id, result }], 'the results are not replaced by the error');
    assert.deepStrictEqual(deleted, [], 'the results are not deleted');
    assert.strictEqual(executor.getCurrentRunningCount('scraper'), 0);
  });

  it('deletes the results of a task deleted while running', async () => {
    const id = await addTask();
    const executor = newExecutor();
    scrape = async () => {
      await db.removeAsync({ id });
      throw new Error('scraper crashed');
    };
    const restoreConsole = silenceConsoleError();
    saved.length = 0;
    deleted.length = 0;
    try {
      await run(executor, id);
    } finally {
      restoreConsole();
    }
    assert.deepStrictEqual(saved, []);
    assert.deepStrictEqual(deleted, [id]);
  });

  it('does not cache the results of a task stopped while running, and caches a finished one', async () => {
    const executor = newExecutor();
    for (const usesPushData of [false, true]) {
      pushDataUsed = usesPushData;
      cached.length = 0;

      const stopped = await addTask();
      scrape = async () => {
        // The user presses Stop while the task runs; the scraper returns what it has
        await updateTask(stopped, { status: TaskStatus.ABORTED });
        return [{ place_id: 'a' }];
      };
      await run(executor, stopped);
      assert.strictEqual(await statusOf(stopped), TaskStatus.ABORTED);
      assert.deepStrictEqual(cached, [], 'partial results must not be served to the next identical search');

      const finished = await addTask();
      scrape = async () => [{ place_id: 'b' }];
      await run(executor, finished);
      assert.strictEqual(await statusOf(finished), TaskStatus.COMPLETED);
      assert.deepStrictEqual(cached, [finished]);
    }
    pushDataUsed = false;
  });
});
