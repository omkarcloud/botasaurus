import { chromium, Browser, BrowserContext, Page } from "rebrowser-playwright-core";
import * as ChromeLauncher from "chrome-launcher";
import * as fs from "fs";
import { execFile } from "child_process";

export type PlaywrightChrome = {
    context: BrowserContext;
    close: () => Promise<void>;
    forceKill: () => void;
    page: Page;
};

// Chrome launches that failed in a row, and the last one's error. The queues
// retry a failed launch for every item and swallow the error, so a Chrome
// that can never start (blocked by security software, a broken install) kept
// a task crawling for hours with no error; callers read this to stop instead.
let consecutiveLaunchFailures = 0;
let lastLaunchError: unknown = null;

export function getChromeLaunchFailures(): { consecutive: number; lastError: unknown } {
    return { consecutive: consecutiveLaunchFailures, lastError: lastLaunchError };
}

export function resetChromeLaunchFailures(): void {
    consecutiveLaunchFailures = 0;
}

// chrome-launcher's kill() is synchronous: on Windows it waits for taskkill and
// then deletes the profile, which froze the whole Electron main thread (UI, API
// and scraping) for 2.6-8 s per Chrome on a busy machine, and browsers are retired
// every few minutes. So this runs taskkill and the delete in the background, and
// keeps the synchronous kill() for when the process is exiting.
const CHROME_EXIT_WAIT_MS = 5000;

function runTaskkill(pid: number) {
    // /T: the whole tree, https://github.com/GoogleChrome/chrome-launcher/issues/266
    return new Promise<void>((resolve) => {
        execFile('taskkill', ['/pid', String(pid), '/T', '/F'], { windowsHide: true }, () => resolve());
    });
}

export function createBackgroundKill(
    launcher: Pick<ChromeLauncher.Launcher, 'chromeProcess' | 'kill' | 'destroyTmp'>,
    { run = runTaskkill, isWindows = process.platform === 'win32', exitWaitMs = CHROME_EXIT_WAIT_MS } = {},
) {
    return async () => {
        const chromeProcess = launcher.chromeProcess;
        if (!isWindows || !chromeProcess?.pid) {
            launcher.kill();
            return;
        }
        const hasExited = () => chromeProcess.exitCode !== null || chromeProcess.signalCode !== null;
        if (!hasExited()) {
            let timer: NodeJS.Timeout | undefined;
            const gone = new Promise<void>((resolve) => {
                chromeProcess.once('exit', () => resolve());
                timer = setTimeout(resolve, exitWaitMs);
            });
            await run(chromeProcess.pid);
            await gone;
            clearTimeout(timer);
            if (!hasExited()) {
                launcher.kill();
                return;
            }
        }
        // kill() with no process only returns, so destroyTmp is called directly
        delete launcher.chromeProcess;
        launcher.destroyTmp();
    };
}

// The fs chrome-launcher deletes the profile with
export function createLauncherFs(isExiting: () => boolean, onRemoval: (removal: Promise<void>) => void = () => {}): typeof fs {
    return {
        ...fs,
        rmSync: (path: fs.PathLike, options?: fs.RmOptions) => {
            if (isExiting()) return fs.rmSync(path, options);
            // A profile left behind by a failed delete is swept at the next start
            onRemoval(fs.promises.rm(path, options).catch(() => {}));
        },
    } as typeof fs;
}

// Every Chrome not closed yet. chrome-launcher's killAll() only knows the ones its
// launch() created, and these must not outlive the process either.
const liveChromes = new Set<() => void>();
process.on('exit', () => killLaunchedChromes());

export function killLaunchedChromes(): void {
    for (const forceKill of Array.from(liveChromes)) {
        forceKill();
    }
}

export async function createPlaywrightChrome(headless: boolean, userAgent:string| null): Promise<PlaywrightChrome> {
    const flags = [
        "--start-maximized",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-service-autorun",
        "--homepage=about:blank",
        "--no-pings",
        "--password-store=basic",
        "--disable-infobars",
        "--disable-breakpad",
        "--disable-dev-shm-usage",
        "--disable-session-crashed-bubble",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-search-engine-choice-screen",
    ];

    if (headless) {
        flags.push("--headless=new");
    }

    if (userAgent) {
        flags.push(`--user-agent=${userAgent}`);
    }
    const hasNoSandbox = process.argv.some(x => x === "--no-sandbox")
    if (hasNoSandbox) { 
        flags.push("--no-sandbox");
    }

    let isExiting = false;
    let profileRemoved: Promise<void> = Promise.resolve();
    const launcher = new ChromeLauncher.Launcher({
        chromeFlags: flags,
        handleSIGINT: false,
    }, { fs: createLauncherFs(() => isExiting, (removal) => { profileRemoved = removal; }) });
    const killInBackground = createBackgroundKill(launcher);
    const forceKill = () => {
        isExiting = true;
        liveChromes.delete(forceKill);
        try { launcher.kill(); } catch {}
    };
    liveChromes.add(forceKill);
    try {
        await launcher.launch();
    } catch (error) {
        forceKill();
        consecutiveLaunchFailures++;
        lastLaunchError = error;
        throw error;
    }
    const port = launcher.port;

    // If anything fails after Chrome has launched (CDP connect timeout,
    // newPage failure), kill the launched Chrome — otherwise it is orphaned
    // forever on about:blank since no PlaywrightChrome handle is ever returned.
    let browser: Browser;
    let context: BrowserContext;
    let page: Page;
    try {
        browser = await chromium.connectOverCDP(`http://localhost:${port}`);
        context = browser.contexts()[0];
        page = await context.newPage();
    } catch (error) {
        await killInBackground().catch(() => {});
        liveChromes.delete(forceKill);
        // A Chrome that starts but can't be connected to is a failed launch
        // too: counting its start as a success reset the count, so a caller
        // never stopped though every item failed
        consecutiveLaunchFailures++;
        lastLaunchError = error;
        throw error;
    }
    consecutiveLaunchFailures = 0;

    return {
        context,
        close: async () => {
            await safeRun(() => context.close());
            await safeRun(() => browser.close());
            await safeRun(killInBackground);
            liveChromes.delete(forceKill);
            // Before the process may exit: half a profile can't be told apart from
            // one in use, so it would never be swept
            await profileRemoved;
        },
        forceKill,
        page,
    };
}

async function safeRun(fn: () => Promise<any>) {
    try {
        await fn();
    } catch (error) {
        console.error(error);
    }
}