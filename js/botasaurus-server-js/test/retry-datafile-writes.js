const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Datastore = require('@seald-io/nedb');
const storage = require('@seald-io/nedb/lib/storage.js');
const { retryTransientWrites } = require('../src/retry-datafile-writes');

const fsError = (code) => Object.assign(new Error(`${code}: open 'db.nedb'`), { code });

async function openDb() {
  const filename = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'nedb-retry-')), 'db.nedb');
  const db = new Datastore({ filename });
  await db.loadDatabaseAsync();
  retryTransientWrites(db, 30, 10);
  return { db, filename };
}

// Makes the next `failures` appends fail with `code`, counting every call
function failAppends(code, failures) {
  const appendFileAsync = storage.appendFileAsync;
  const calls = { count: 0 };
  storage.appendFileAsync = (...args) => {
    calls.count++;
    if (failures-- > 0) return Promise.reject(fsError(code));
    return appendFileAsync(...args);
  };
  return { calls, restore: () => { storage.appendFileAsync = appendFileAsync; } };
}

describe('retryTransientWrites', () => {
  it('retries an append that fails while another program holds the datafile', async () => {
    const { db, filename } = await openDb();
    const append = failAppends('EBUSY', 2);
    try {
      await db.insertAsync({ id: 1, status: 'pending' });
    } finally {
      append.restore();
    }
    assert.strictEqual(append.calls.count, 3);
    assert.match(fs.readFileSync(filename, 'utf8'), /"id":1/);
  });

  it('does not retry other write errors', async () => {
    const { db } = await openDb();
    const append = failAppends('ENOSPC', Infinity);
    try {
      await assert.rejects(db.insertAsync({ id: 2 }), /ENOSPC/);
    } finally {
      append.restore();
    }
    assert.strictEqual(append.calls.count, 1);
  });
});
