import {
    isErrorsInstance,
    NotFoundException,
    formatExc,
    printExc,
    sleep,
} from "./utils";
import { prompt } from "./beep-utils";
import { isDontCache } from "./dontcache";
import pLimit from "p-limit";
import { Page, BrowserContext } from "rebrowser-playwright-core";
import { ChromeNotInstalledError } from 'chrome-launcher/dist/utils';

import {
    printRunning,
    writeOutput,
    IS_PRODUCTION,
    saveErrorLogs,
} from "./decorators-common";
import { increment } from "./increment";
import { isNotEmptyString } from "./string-utils";
import {
    CacheMissException,
    writeJson,
    createCacheDirectoryIfNotExists,
    _getCachePath,
    _has,
    _get,
    _remove,
} from "./cache";
import { FormatType } from "./formats";
import { createPlaywrightChrome, PlaywrightChrome } from "./page";
import { getBotasaurusStorage } from "./botasaurus-storage"
import { determineMaxLimit, drainQueue, getItemRepr, removeItemFromSeenItemsSet, TaskRunOptions } from "./task"



type PlaywrightRunOptions<I = any> = TaskRunOptions<I> & {
    page: Page;
    context: BrowserContext;
    
};

type PlaywrightOptions<I> = {
    name?: string;
    parallel?: number | ((data: any) => number);
    metadata?: any;
    cache?: true | false | "REFRESH";
    closeOnCrash?: boolean;
    output?: string | ((data: any, result: any) => void) | null;
    outputFormats?: FormatType[];
    raiseException?: boolean;
    mustRaiseExceptions?: any[];
    run: (options: PlaywrightRunOptions<I>) => any;
    maxRetry?: number;
    retryWait?: number;
    createErrorLogs?: boolean;
    // SKIP THESE
    // Browser behavior options [LATER]
    // blockImages?: boolean;
    // blockImagesAndCss?: boolean;
    // windowSize?: ((data: any) => string) | string;
    // tinyProfile?: boolean;
    // waitForCompletePageLoad?: boolean;
    // addArguments?: string[] | ((data: any, args: string[]) => void);
    // extensions?: any[] | ((data: any) => any[]);
    // lang?: ((data: any) => string) | string;
    headless?: ((data: any) => boolean) | boolean;

    // System behavior [LATER]
    // beep?: boolean;

    // Browser profile and identity [LATER]
    // profile?: ((data: any) => string) | string;
    // proxy?: ((data: any) => string) | string;
    userAgent?: ((data: any) => string) | string;

    // Driver options
    reuseDriver?: boolean;
    // createDriver?: () => Driver;
};
const closeDriver = async (driver: PlaywrightChrome | null) => {
    try {
        if (driver) {
            await driver.close();
        }
    } catch (error) {
        throw error;
    }
};

const closeDriverPool = async (pool: (PlaywrightChrome | null)[]) => {
    if (pool.length === 1) {
        await closeDriver(pool[0]);
        pool.length = 0;
    } else if (pool.length > 0) {
        while (pool.length > 0) {
            await closeDriver(pool.pop() as PlaywrightChrome);
        }
    }
};

function chromeNotInstalledError() {
    getBotasaurusStorage().setItem("isChromeInstalled", false )
    return new Error('Google Chrome is not installed on your system. This tool requires Google Chrome to run. Please visit https://www.google.com/chrome/ to download and install Google Chrome.');
}
let isChromeInstalled = true;

function createPlaywright<I>(
    options: PlaywrightOptions<I>,
    is_async_queue: boolean
) {
    const _driverPool: PlaywrightChrome[] = [];

    const performPlaywright = async function (
        data: any = null,
        overrideOptions: Omit<PlaywrightOptions<any>, "run"> = {}
    ) {
        const combined = { ...options, ...overrideOptions };
        printRunning();
        if (!isChromeInstalled) {
            throw chromeNotInstalledError();
        }

        let {
            parallel = 1,
            name = null,
            run,
            metadata = null,
            cache = null,
            // beep = false,
            closeOnCrash = false,
            output = "default",
            outputFormats = null,
            raiseException = false,
            mustRaiseExceptions = null,
            maxRetry = null,
            retryWait = null,
            createErrorLogs = true,
            reuseDriver = false,
            headless = false, 
            userAgent = null
        } = combined;

        performPlaywright.__name__ = isNotEmptyString(name)
            ? name!.trim()
            : performPlaywright.__name__;
        // @ts-ignore
        const returnDontCacheAsIs = combined.returnDontCacheAsIs;
        // @ts-ignore
        const isAborted = combined.isAborted ?? (() => false);
        // @ts-ignore 
        const pushData = combined.pushData ?? (() => {});
        const fn_name = performPlaywright.__name__;

        if (cache) {
            createCacheDirectoryIfNotExists(fn_name);
        }

        async function runPlaywright(
            data: any,
            retryAttempt: number,
            retryDriver: PlaywrightChrome | null = null
        ): Promise<any> {
            let path: string | undefined;

            if (cache === true) {
                path = _getCachePath(fn_name, data);
                if (_has(path)) {
                    try {
                        return _get(path);
                    } catch (error) {
                        if (!(error instanceof CacheMissException)) throw error;
                    }
                }
            } else if (cache === "REFRESH") {
                path = _getCachePath(fn_name, data);
            }

            let result: any;
            const evaluated_headless = typeof headless === "function" ? headless(data) : headless;
            const evaluated_userAgent = typeof userAgent === "function" ? userAgent(data) : userAgent;
            // @ts-ignore
            let driver: PlaywrightChrome | null = null;
            try {
                if (retryDriver !== null) {
                    driver = retryDriver;
                } else if (reuseDriver && _driverPool.length > 0) {
                    driver = (_driverPool.pop() || null) as PlaywrightChrome;
                } else {
                    // MAKE ONE HERE ADD
                    driver = await createPlaywrightChrome(evaluated_headless, evaluated_userAgent);
                }

                if (maxRetry !== undefined && maxRetry !== null) {
                    // Set retry-related configurations
                    // ...
                }

                result = await run({ data, metadata, isAborted, pushData, ...driver });
                if (result === undefined) {
                    result = null;
                }

                if (reuseDriver) {
                    _driverPool.push(driver);
                } else {
                    await closeDriver(driver);
                }

                if (cache === true || cache === "REFRESH") {
                    if (isDontCache(result)) {
                        _remove(path!);
                    } else {
                        writeJson(result, path!);
                    }
                }

                if (isDontCache(result)) {
                    if (!returnDontCacheAsIs) {
                        result = result.data;
                    }
                }
                return result;
            } catch (error) {
                if (error instanceof ChromeNotInstalledError) {
                    isChromeInstalled = false;
                    throw chromeNotInstalledError();
                }

                if (error instanceof NotFoundException && !error.raisedOnce) {
                    if (error.raiseMaximum1Time) {
                        error.raisedOnce = true;
                    }
                    if (!reuseDriver) {
                        await closeDriver(driver);
                    }
                    throw error;
                } else if (
                    mustRaiseExceptions &&
                    isErrorsInstance(mustRaiseExceptions, error)[0]
                ) {
                    if (createErrorLogs) {
                        saveErrorLogs(formatExc(error), data);
                    }
                    await closeDriver(driver);
                    throw error;
                }

                if (
                    maxRetry !== undefined &&
                    maxRetry !== null &&
                    maxRetry > retryAttempt
                ) {
                    printExc(error);
                    await closeDriver(driver);
                    if (retryWait) {
                        console.log(`Waiting for ${retryWait} seconds`);
                        await sleep(retryWait);
                    }
                    return runPlaywright(data, retryAttempt + 1);
                }

                if (!raiseException) {
                    printExc(error);
                }

                console.error("Playwright failed for input:", data);
                if (createErrorLogs) {
                    saveErrorLogs(formatExc(error), data);
                }

                if (!IS_PRODUCTION) {
                    if (raiseException) {
                        printExc(error);
                    }

                    if (!closeOnCrash) {
                        await prompt(
                            "We've paused the browser to help you debug. Press 'Enter' to close."
                        );
                    }
                }

                await closeDriver(driver);

                if (raiseException) {
                    throw error;
                }

                return result;
            }
        }

        const numberOfWorkers =
            typeof parallel === "function" ? parallel(data) : parallel;

        if (
            numberOfWorkers !== undefined &&
            numberOfWorkers !== null &&
            typeof numberOfWorkers !== "number"
        ) {
            throw new Error("parallel Option must be a number");
        }

        let usedData = data === undefined ? null : data;

        usedData = typeof usedData === "function" ? usedData() : usedData;
        const originalData = usedData;

        let returnFirst = false;
        if (!Array.isArray(usedData)) {
            returnFirst = true;
            usedData = [usedData];
        }
        // @ts-ignore
        const hasNumberOfWorkers = numberOfWorkers !== undefined && numberOfWorkers !== null && numberOfWorkers !== false;
        const n =
            !hasNumberOfWorkers || numberOfWorkers <= 1
                ? 1
                : Math.min(usedData.length, numberOfWorkers);
        let result: any[] = [];

        if (n <= 1) {
            for (let index = 0; index < usedData.length; index++) {
                const dataItem = usedData[index];
                const currentResult = await runPlaywright(dataItem, 0);
                result.push(currentResult);
            }
        } else {
            if (typeof parallel === "function") {
                console.log(`Running ${n} Requests in Parallel`);
            }
            const limit = pLimit(n);
            const promises = usedData.map((dataItem: any) =>
                limit(async () => {
                    const currentResult = await runPlaywright(dataItem, 0);
                    return currentResult;
                })
            );

            result = await Promise.all(promises);
        }

        if (!reuseDriver) {
            await closeDriverPool(_driverPool);
        }

        if (returnFirst) {
            let final = result[0];
            if (!is_async_queue) {
                writeOutput(
                    output,
                    outputFormats,
                    originalData,
                    final,
                    fn_name
                );
                return final;
            }
            return { originalData, result: final };
        } else {
            let final = result;

            if (!is_async_queue) {
                writeOutput(
                    output,
                    outputFormats,
                    originalData,
                    final,
                    fn_name
                );
                return final;
            }
            return { originalData, result: final };
        }
    };
    performPlaywright._driver_pool = _driverPool; // Ensure

    performPlaywright._scraperType = "browser";
    const current = increment();
    performPlaywright.__name__ = isNotEmptyString(options.name)
        ? options.name!.trim()
        : current;

    performPlaywright.close = async () => {
        await closeDriverPool(_driverPool);
    };

    return performPlaywright;
}

export function playwright<I = any>(options: PlaywrightOptions<I>) {
    return createPlaywright<I>(options, false);
}

export function playwrightQueue<I = any>(
    options: PlaywrightOptions<I> & { sequential?: boolean }
) {
    // Extract parallel from options - it controls queue-level concurrency, not passed to createPlaywright
    const { parallel: parallelOption, ...playwrightOptions } = options
    const run = createPlaywright<I>(playwrightOptions as PlaywrightOptions<I>, true);
    const performPlaywright = () => {
        let seenItems = new Set();
        let lastPromise: Promise<any> = Promise.resolve();
        const state = { promises: [] as any[], draining: false };
        let sequential = "sequential" in options ? options.sequential : false;
        
        // Create concurrency limiter for parallel mode
        const maxLimit = determineMaxLimit(parallelOption)

        let limit: pLimit.Limit
        if (maxLimit <= 1) {
            sequential = true
        } else {
            limit = pLimit(maxLimit)
        }

        function getUnique(items: any[]) {
            let singleItem = false;
            if (!Array.isArray(items)) {
                items = [items];
                singleItem = true;
            }

            let newItems = [];

            for (let item of items) {
                const itemRepr = getItemRepr(item);

                if (!seenItems.has(itemRepr)) {
                    newItems.push(item);
                    seenItems.add(itemRepr);
                }
            }

            return singleItem && newItems.length ? newItems[0] : newItems;
        }

        const cleanup = () => {
            state.promises = [];
            state.draining = false;
            seenItems.clear();
            lastPromise = Promise.resolve();
        };

        return {
            put: function (
                data: any,
                overrideOptions: Omit<PlaywrightOptions<any>, "run"> = {}
            ) {
                const uniqueData = getUnique(data);
                let promise: Promise<any>;
                if (sequential) {
                    // runs sequentially
                    promise = lastPromise.then(() =>
                        run(uniqueData, overrideOptions)
                    );
                    lastPromise = promise;

                    state.promises.push(promise);
                    return promise.then((x) => x.result);
                } else {
                    if (Array.isArray(uniqueData)) {
                        promise = Promise.all(uniqueData.map(x => limit(() => run(x, overrideOptions))))
                        state.promises.push(promise.then(results => ({ originalData: uniqueData, result: results.map((x: any) => x.result) })))
                        return promise.then(results => results.map((x: any) => x.result))
                    } else {
                        promise = limit(() => run(uniqueData, overrideOptions))
                        
                        state.promises.push(promise)
                        return promise.then((x) => x.result);
                    }
                }
            },
            get: async function (n: number | null = null) {
                return drainQueue(state, cleanup, (items) => removeItemFromSeenItemsSet(items, seenItems), options, run.__name__, n);
            },
            isCompleted: function () {
                return state.promises.length === 0 && !state.draining;
            },
            close: async () => {
                await run.close();
            },
        };
    };
    performPlaywright._isQueue = true;
    return performPlaywright;
}
