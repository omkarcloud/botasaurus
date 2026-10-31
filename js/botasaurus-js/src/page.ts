import { chromium, Browser, BrowserContext, Page } from "rebrowser-playwright-core";
import * as ChromeLauncher from "chrome-launcher";

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

    let launched: ChromeLauncher.LaunchedChrome;
    try {
        launched = await ChromeLauncher.launch({
            chromeFlags: flags,
            handleSIGINT: false,
        });
    } catch (error) {
        consecutiveLaunchFailures++;
        lastLaunchError = error;
        throw error;
    }
    const { port, kill } = launched;

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
        try { kill(); } catch {}
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
            // @ts-ignore
            await safeRun(() => kill());
        },
        forceKill: () => {
            try { kill(); } catch {}
        },
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