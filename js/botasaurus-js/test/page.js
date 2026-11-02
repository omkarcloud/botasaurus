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
let launcherKills = 0;
stub('chrome-launcher', {
  Launcher: class {
    port = 9222;
    async launch() {
      if (!launchWorks) throw new Error('connect ECONNREFUSED 127.0.0.1:58924');
    }
    kill() { launcherKills++; }
    destroyTmp() {}
  },
});
stub('rebrowser-playwright-core', {
  chromium: { connectOverCDP: async () => ({ close: async () => {}, contexts: () => [{ newPage: async () => ({}) }] }) },
});

const fs = require('fs');
const os = require('os');
const { EventEmitter } = require('events');
const { createPlaywrightChrome, getChromeLaunchFailures, resetChromeLaunchFailures, createBackgroundKill, createLauncherFs, killLaunchedChromes } = require(path.join(src, 'page'));

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

describe('closing a Chrome', () => {
  // A launcher whose process exits when taskkill runs, unless told it will not
  function fakeLauncher({ exitsOnTaskkill = true, exitCode = null } = {}) {
    const chromeProcess = Object.assign(new EventEmitter(), { pid: 1234, exitCode, signalCode: null });
    const calls = [];
    const launcher = { chromeProcess, kill: () => calls.push('kill'), destroyTmp: () => calls.push('destroyTmp') };
    const run = async (pid) => {
      calls.push(`taskkill ${pid}`);
      if (exitsOnTaskkill) {
        chromeProcess.exitCode = 1;
        chromeProcess.emit('exit');
      }
    };
    return { launcher, calls, run };
  }

  it('on Windows runs taskkill without the blocking kill()', async () => {
    const { launcher, calls, run } = fakeLauncher();
    await createBackgroundKill(launcher, { run, isWindows: true })();
    assert.deepStrictEqual(calls, ['taskkill 1234', 'destroyTmp']);
    assert.strictEqual(launcher.chromeProcess, undefined);
  });

  it('falls back to kill() if Chrome is still running after taskkill', async () => {
    const { launcher, calls, run } = fakeLauncher({ exitsOnTaskkill: false });
    await createBackgroundKill(launcher, { run, isWindows: true, exitWaitMs: 1 })();
    assert.deepStrictEqual(calls, ['taskkill 1234', 'kill']);
  });

  it('a Chrome that has already exited only has its files cleaned up', async () => {
    const { launcher, calls, run } = fakeLauncher({ exitCode: 0 });
    await createBackgroundKill(launcher, { run, isWindows: true })();
    assert.deepStrictEqual(calls, ['destroyTmp']);
  });

  it('other platforms use kill(), which does not block on a child process there', async () => {
    const { launcher, calls, run } = fakeLauncher();
    await createBackgroundKill(launcher, { run, isWindows: false })();
    assert.deepStrictEqual(calls, ['kill']);
  });

  const tempProfile = () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'page-test-'));
    fs.writeFileSync(path.join(dir, 'Cookies'), 'x');
    return dir;
  };

  it('deletes the profile in the background', async () => {
    const dir = tempProfile();
    createLauncherFs(() => false).rmSync(dir, { recursive: true, force: true });
    assert.strictEqual(fs.existsSync(dir), true);
    for (let i = 0; i < 100 && fs.existsSync(dir); i++) await new Promise((r) => setTimeout(r, 10));
    assert.strictEqual(fs.existsSync(dir), false);
  });

  it('a Chrome that was not closed is killed on shutdown, once', async () => {
    launchWorks = true;
    killLaunchedChromes();
    launcherKills = 0;
    await createPlaywrightChrome(true, null);
    killLaunchedChromes();
    assert.strictEqual(launcherKills, 1);
    killLaunchedChromes();
    assert.strictEqual(launcherKills, 1);
  });

  it('a closed Chrome is not killed again on shutdown', async () => {
    launchWorks = true;
    killLaunchedChromes();
    const chrome = await createPlaywrightChrome(true, null);
    chrome.context.close = async () => {};
    await chrome.close();
    launcherKills = 0;
    killLaunchedChromes();
    assert.strictEqual(launcherKills, 0);
  });

  it('waits for the profile delete through its callback', async () => {
    const dir = tempProfile();
    let removal;
    createLauncherFs(() => false, (r) => { removal = r; }).rmSync(dir, { recursive: true, force: true });
    await removal;
    assert.strictEqual(fs.existsSync(dir), false);
  });

  it('deletes the profile at once when the process is exiting', () => {
    const dir = tempProfile();
    createLauncherFs(() => true).rmSync(dir, { recursive: true, force: true });
    assert.strictEqual(fs.existsSync(dir), false);
  });
});
