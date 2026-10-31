// chrome-launcher and Playwright are replaced in the require cache, so no
// Chrome is started.
const assert = require('assert');
const path = require('path');

const src = path.join(__dirname, '..', 'src');

let launchWorks = false;
function stub(request, exports) {
  const filename = require.resolve(request, { paths: [src] });
  require.cache[filename] = { id: filename, filename, loaded: true, exports };
}
stub('chrome-launcher', {
  launch: async () => {
    if (!launchWorks) throw new Error('connect ECONNREFUSED 127.0.0.1:58924');
    return { port: 9222, kill: () => {} };
  },
});
stub('rebrowser-playwright-core', {
  chromium: { connectOverCDP: async () => ({ contexts: () => [{ newPage: async () => ({}) }] }) },
});

const { createPlaywrightChrome, getChromeLaunchFailures, resetChromeLaunchFailures } = require(path.join(src, 'page'));

describe('Chrome launch failures', () => {
  beforeEach(() => resetChromeLaunchFailures());

  it('counts launches that fail in a row and keeps the last error', async () => {
    launchWorks = false;
    for (let i = 1; i <= 3; i++) {
      await assert.rejects(createPlaywrightChrome(true, null), /ECONNREFUSED/);
      assert.strictEqual(getChromeLaunchFailures().consecutive, i);
    }
    assert.match(String(getChromeLaunchFailures().lastError.message), /ECONNREFUSED 127\.0\.0\.1:58924/);
  });

  it('a launch that works clears the count, and so does a reset', async () => {
    launchWorks = false;
    await assert.rejects(createPlaywrightChrome(true, null));
    launchWorks = true;
    await createPlaywrightChrome(true, null);
    assert.strictEqual(getChromeLaunchFailures().consecutive, 0);

    launchWorks = false;
    await assert.rejects(createPlaywrightChrome(true, null));
    resetChromeLaunchFailures();
    assert.strictEqual(getChromeLaunchFailures().consecutive, 0);
  });
});
