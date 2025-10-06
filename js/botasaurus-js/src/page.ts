import { chromium, BrowserContext, Page } from "rebrowser-playwright-core";
import * as ChromeLauncher from "chrome-launcher";

export type PlaywrightChrome = {
    context: BrowserContext;
    close: () => Promise<void>;
    page: Page;
};

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

    const { port, kill } = await ChromeLauncher.launch({
        chromeFlags: flags,
    });

    const browser = await chromium.connectOverCDP(`http://localhost:${port}`);
    const context = browser.contexts()[0];
    const page = await context.newPage();

    return {
        context,
        close: async () => {
            await safeRun(() => context.close());
            await safeRun(() => browser.close());
            // @ts-ignore
            await safeRun(() => kill());
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