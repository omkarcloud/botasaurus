import fastify, { FastifyInstance, FastifyRequest } from "fastify";
import {
    createAsyncTask,
    createSyncTask,
    getTasks,
    getTask,
    getTaskResults,
    downloadTaskResults,
    abortSingleTask,
    deleteSingleTask,
    bulkAbortTasks,
    bulkDeleteTasks,
    getAppProps,
    isAnyTaskUpdated,
    isTaskUpdated,
    getTasksForUiDisplay,
    patchTask,
    getUiTaskResults,
} from "./task-routes";
import { getExecutor } from "./executor";
import { Server } from "./server";
import { kebabCase } from "change-case";
import { 
    validateDirectCallRequest, 
    validateScraperTypeParam, 
    validateScraperNameParam, 
    validateMaxTasksParam, 
    validateTaskIdInPayload, 
    validateInProgressTaskIds 
} from "./validation";
import { sleep } from "botasaurus/utils";
import { DirectCallCacheService } from "./task-results";
import { cleanBasePath, isNotEmptyObject, isObject } from "./utils";
import { isDontCache } from "botasaurus/dontcache";
import { JsonHTTPResponseWithMessage } from "./errors";
import { cleanDataInPlace } from "botasaurus/output";
import { db, removeDuplicatesByKey } from "./models";
import { DEFAULT_TASK_TIMEOUT, MasterExecutor, TaskCompletionPayload, TaskFailurePayload, PushDataChunkPayload, PushDataCompletePayload } from "./master-executor";
import { WorkerExecutor } from "./worker-executor";
import { isMaster, isWorker } from "./env"

/**
 * Node role in K8s deployment
 */
type NodeRole = 'master' | 'worker' | 'standalone';

/**
 * Check if a string is a valid URL
 */
function isValidUrl(urlString: string): boolean {
    try {
        new URL(urlString);
        return true;
    } catch {
        return false;
    }
}

/**
 * Parse command line arguments for --master or --worker flags
 */

/**
 * Check master endpoint health, retrying up to 3 times.
 */
async function checkMasterHealth(masterEndpoint: string) {
    const MAX_RETRIES = 3;
    let retryCount = 0;
    while (retryCount < MAX_RETRIES) {
        retryCount++;
        try {
            const response = await fetch(`${masterEndpoint}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });

            if (!response.ok) {
                throw new Error(`Health check returned status ${response.status}`);
            }
            if (retryCount > 1) {
                console.debug(`[K8s] Successfully reached master after retry (attempt ${retryCount}/${MAX_RETRIES}): ${masterEndpoint}`);
            }
            return true;
        } catch (error: any) {
            console.error(error);
            console.debug(`[K8s] Health check error (attempt ${retryCount}/${MAX_RETRIES}): ${error instanceof Error ? error.message : error} - ${masterEndpoint}`);
            if (retryCount < MAX_RETRIES) {
                // Wait briefly before retrying
                await sleep(3);
                continue;
            }
        }
    }

    console.error(`[K8s] Failed to reach master after ${MAX_RETRIES} attempts: ${masterEndpoint}`);
    if (!ApiConfig.isMasterNode()) {
        // If not master node, exit the process
        process.exit(1);
    }
    return false;
}


function addCorsHeaders(reply: any) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    );
    reply.header(
        "Access-Control-Allow-Headers",
        "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    );
}

function addScraperRoutes(app: FastifyInstance, apiBasePath: string) {
    Object.values(Server.scrapers).forEach((scraper) => {
        // Get the main route path
        const routePath = `${apiBasePath}/${kebabCase(scraper.scraper_name)}`;
        const fn = scraper.function;
        const key = Server.isScraperBasedRateLimit
            ? scraper.scraper_name
            : scraper.scraper_type;

        const scrapingFunction = async (request: any, reply: any) => {
            try {
                const params: Record<string, any> = {};
                for (const [key, value] of Object.entries(
                    request.query as any
                )) {
                    if (key.endsWith("[]")) {
                        params[key.slice(0, -2)] = Array.isArray(value)
                            ? value
                            : [value];
                    } else {
                        params[key] = value;
                    }
                }

                // Validate params against scraper's input definition
                const [validatedData, metadata, enableCache] = validateDirectCallRequest(
                    scraper.scraper_name,
                    params
                );

                // Check if scraper has split_task
                const splitTask = scraper.split_task;
                const scraperName = scraper.scraper_name;

                // If split_task exists, split the data
                let dataItems: any[];
                if (splitTask) {
                    dataItems = await splitTask(validatedData);
                } else {
                    dataItems = [validatedData];
                }

                const mt = isNotEmptyObject(metadata) ? { metadata } : {};
                let shouldDecrementCapacity = false;

                function restoreCapacity() {
                    if (shouldDecrementCapacity) {
                        getExecutor().decrementCapacity(key);
                        shouldDecrementCapacity = false;
                    }
                }

                // Collect results with metadata
                let collectedResults: Array<{
                    isFromCache: boolean;
                    isDontCache: boolean;
                    result: any;
                    cacheKey?: string;
                }> = [];
                try {
                    // Execute function for each data item
                    for (const dataItem of dataItems) {
                        let cacheKey: string | undefined;
                        let isFromCache = false;
                        let resultData: any = null;
                        let isDontCacheFlag = false;

                        // Check cache for this specific data item
                        if (enableCache) {
                            cacheKey = DirectCallCacheService.createCacheKey(
                                scraperName,
                                dataItem
                            );

                            if (DirectCallCacheService.has(cacheKey)) {
                                try {
                                    resultData = DirectCallCacheService.get(
                                        cacheKey
                                    );
                                    isFromCache = true;
                                } catch (error) {
                                    console.error(error);
                                    // Continue with normal execution if cache fails
                                }
                            }
                        }

                        // Execute if not from cache
                        if (!isFromCache) {
                            // Wait for capacity if needed (only on first execution)
                            if (!shouldDecrementCapacity) {
                                while (!getExecutor().hasCapacity(key)) {
                                    await sleep(0.1);
                                }
                                getExecutor().incrementCapacity(key);
                                shouldDecrementCapacity = true;
                            }

                            const result = await fn(dataItem, {
                                ...mt,
                                parallel: null,
                                cache: false,
                                beep: false,
                                raiseException: true,
                                closeOnCrash: true,
                                output: null,
                                createErrorLogs: false,
                                returnDontCacheAsIs: true,
                            });

                            // Handle don't cache flag
                            if (isDontCache(result)) {
                                isDontCacheFlag = true;
                                resultData = result.data;
                            } else {
                                resultData = result;
                            }
                        }

                        // Collect result
                        collectedResults.push({
                            isFromCache,
                            isDontCache: isDontCacheFlag,
                            result: resultData,
                            cacheKey,
                        });
                    }
                } finally {
                    restoreCapacity();
                }

                // Determine if we should return first object
                const firstResult =
                    collectedResults.length > 0
                        ? collectedResults[0].result
                        : null;
                const returnFirstObject = !splitTask && isObject(firstResult);

                if (enableCache) {
                    // Handle caching for each item
                    for (const item of collectedResults) {
                        // Skip if from cache or don't cache
                        if (item.isFromCache || item.isDontCache) {
                            continue;
                        }

                        // If not an object, clean and remove duplicates
                        if (!isObject(item.result)) {
                            item.result = cleanDataInPlace(item.result);
                            const removeDuplicatesBy =
                                Server.getRemoveDuplicatesBy(scraperName);
                            if (removeDuplicatesBy) {
                                item.result = removeDuplicatesByKey(
                                    item.result,
                                    removeDuplicatesBy
                                );
                            }
                        }

                        // Save to cache
                        if (item.cacheKey) {
                            try {
                                DirectCallCacheService.put(
                                    item.cacheKey,
                                    item.result
                                );
                            } catch (cacheError) {
                                console.error(
                                    "Cache storage error:",
                                    cacheError
                                );
                            }
                        }
                    }
                }

                if (returnFirstObject) {
                    return collectedResults[0].result;
                }

                // Aggregate all results
                let aggregatedResults: any[] = [];
                for (const item of collectedResults) {
                    if (Array.isArray(item.result)) {
                        aggregatedResults.push(...item.result);
                    } else {
                        aggregatedResults.push(item.result);
                    }
                }
                // Release references, else cleanDataInPlace will be useless due to double references
                collectedResults = []
                // Final pass: clean and remove duplicates
                aggregatedResults = cleanDataInPlace(aggregatedResults);
                const removeDuplicatesBy =
                    Server.getRemoveDuplicatesBy(scraperName);
                if (removeDuplicatesBy) {
                    aggregatedResults = removeDuplicatesByKey(
                        aggregatedResults,
                        removeDuplicatesBy
                    );
                }

                return aggregatedResults;
            } catch (error: any) {
                if (error instanceof JsonHTTPResponseWithMessage) {
                    throw error; // Re-throw the error to be handled elsewhere
                }
                console.error("Scraping failed:", error);
                return reply.status(500).send({
                    error: "Scraping failed",
                    message: error.message,
                });
            }
        };

        // Register main route
        app.get(routePath, scrapingFunction);

        // Get any aliases for this scraper
        const aliases = ApiConfig.routeAliases.get(scraper.function) || [];

        // Register all aliases if they exist
        if (aliases.length > 0) {
            aliases.forEach((alias) => {
                const fullAliasPath = `${apiBasePath}${alias}`;
                app.get(fullAliasPath, scrapingFunction);
            });
        }
    });
}

/**
 * Register Kubernetes master routes
 */
function registerMasterRoutes(app: FastifyInstance) {
    // Acquire tasks by scraper type (GET request)
    app.get('/k8s/acquire-tasks-by-type', async (request: FastifyRequest<{ Querystring: { scraper_type: string; max_tasks: string } }>, _) => {
        const { scraper_type: scraperTypeRaw, max_tasks: maxTasksStr } = request.query;
        const scraperType = validateScraperTypeParam(scraperTypeRaw);
        const maxTasks = validateMaxTasksParam(maxTasksStr);

        const executor = getExecutor() as MasterExecutor;
        const tasks = await executor.acquireTasksByScraperType(scraperType, maxTasks);
        return { tasks };
    });

    // Acquire tasks by scraper name (GET request)
    app.get('/k8s/acquire-tasks-by-name', async (request: FastifyRequest<{ Querystring: { scraper_name: string; max_tasks: string } }>, _) => {
        const { scraper_name: scraperNameRaw, max_tasks: maxTasksStr } = request.query;
        const scraperName = validateScraperNameParam(scraperNameRaw);
        const maxTasks = validateMaxTasksParam(maxTasksStr);

        const executor = getExecutor() as MasterExecutor;
        const tasks = await executor.acquireTasksByScraperName(scraperName, maxTasks);
        return { tasks };
    });

    // Task completed endpoint
    app.post('/k8s/task-completed', async (request: FastifyRequest<{ Body: TaskCompletionPayload }>, _) => {
        const payload = request.body;
        validateTaskIdInPayload(payload.taskId);

        const executor = getExecutor() as MasterExecutor;
        return executor.handleTaskCompletion(payload);
    });

    // Task failed endpoint
    app.post('/k8s/task-failed', async (request: FastifyRequest<{ Body: TaskFailurePayload }>, _) => {
        const payload = request.body;
        validateTaskIdInPayload(payload.taskId);

        const executor = getExecutor() as MasterExecutor;
        return executor.handleTaskFailure(payload);
    });

    // Worker shutdown endpoint
    app.post('/k8s/worker-shutdown', async (request: FastifyRequest<{ Body: { inProgressTaskIds: number[] } }>, _) => {
        const taskIds = validateInProgressTaskIds(request.body?.inProgressTaskIds);

        const executor = getExecutor() as MasterExecutor;
        return executor.handleWorkerShutdown(taskIds);
    });

    // Check abortion status for multiple tasks (used by workers)
    app.post('/k8s/check-abortion-status', async (request: FastifyRequest<{ Body: { taskIds: number[] } }>, _) => {
        const taskIds = request.body?.taskIds || [];
        
        const executor = getExecutor() as MasterExecutor;
        const results = await executor.getTasksAbortionResults(taskIds);
        return results;
    });

    // PushData chunk endpoint - receives data chunks from workers
    app.post('/k8s/push-data-chunk', async (request: FastifyRequest<{ Body: PushDataChunkPayload }>, _) => {
        const payload = request.body;
        validateTaskIdInPayload(payload.taskId);

        const executor = getExecutor() as MasterExecutor;
        return executor.handlePushDataChunk(payload);
    });

    // PushData complete endpoint - finalizes task after all chunks sent
    app.post('/k8s/push-data-complete', async (request: FastifyRequest<{ Body: PushDataCompletePayload }>, _) => {
        const payload = request.body;
        validateTaskIdInPayload(payload.taskId);

        const executor = getExecutor() as MasterExecutor;
        return executor.handlePushDataComplete(payload);
    });
}

/**
 * Register health endpoint
 */
function registerHealthEndpoint(app: FastifyInstance) {
    app.get('/health', async (_, reply) => {
        // Check if worker is shutting down
        if (ApiConfig.isWorkerNode()) {
            const executor = getExecutor() as WorkerExecutor;
            if (executor.isShuttingDown) {
                return reply.status(503).send({ status: 'shutting_down' });
            }
        }
        try {
            await db.countAsync({});
            return { status: 'ok' };
        } catch (_) {
            return reply.status(503).send({ status: 'database_unreachable' });
        }
    });
}

export function buildApp(
    scrapers: any[],
    apiBasePath: string,
    routeAliases: any,
    enable_cache: boolean
): FastifyInstance {
    const app = fastify({
        logger: true,
        // TODO: change appropriately as needed
        bodyLimit: 500 * 1024 * 1024 // 500MB
    });

    // Add CORS handling
    app.addHook("onRequest", (request, reply, done) => {
        if (request.method === "OPTIONS") {
            addCorsHeaders(reply);
            return reply.send();
        }
        return done();
    });
    app.addHook("onSend", async (_, reply, payload) => {
        addCorsHeaders(reply);
        return payload;
    });
    // Add error handler for JsonHTTPResponseWithMessage
    app.setErrorHandler((error:any, _, reply) => {
        if (error instanceof JsonHTTPResponseWithMessage) {
            reply.code(error.status).headers(error.headers).send(error.body);
        } else {
            console.error(error);
            // Default error handling
            reply.status(500).send({
                message: error.message || "Internal Server Error",
            });
        }
    });

    // Register health endpoint (always available)
    registerHealthEndpoint(app);

    // Register K8s master routes if this is the master node
    if (ApiConfig.isMasterNode()) {
        registerMasterRoutes(app);
    }

    // Routes
    app.get(apiBasePath || "/", (_, reply) => {
        const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><link rel="icon" href="https://botasaurus-api.omkar.cloud/favicon.ico"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#000000"><meta name="description" content="API documentation for using web scrapers"><link rel="apple-touch-icon" href="https://botasaurus-api.omkar.cloud/logo192.png"><title>Api Docs</title><script>window.enable_cache=${enable_cache};window.scrapers=${JSON.stringify(
            scrapers
        )};window.apiBasePath="${
            apiBasePath || ""
        }";window.routeAliases=${JSON.stringify(
            routeAliases
        )};</script><script defer="defer" src="https://botasaurus-api.omkar.cloud/static/js/main.e8772f3d.js"></script><link href="https://botasaurus-api.omkar.cloud/static/css/main.69260e80.css" rel="stylesheet"></head><body><noscript>You need to enable JavaScript to run this app.</noscript><div id="root"></div></body></html>`;

        return reply.type("text/html").send(html);
    });

    app.post(`${apiBasePath}/tasks/create-task-async`, async (request, _) => {
        const jsonData = request.body;
        const result = await createAsyncTask(jsonData);
        return result;
    });

    app.post(`${apiBasePath}/tasks/create-task-sync`, async (request, _) => {
        const jsonData = request.body;
        const result = await createSyncTask(jsonData);
        return result;
    });

    app.get(`${apiBasePath}/tasks`, async (request, _) => {
        const queryParams = request.query;
        const result = await getTasks(queryParams);
        return result;
    });

    app.get(
        `${apiBasePath}/tasks/:taskId`,
        async (request: FastifyRequest<{ Params: { taskId: number } }>, _) => {
            const taskId = request.params.taskId;
            const result = await getTask(taskId);
            return result;
        }
    );

    app.post(
        `${apiBasePath}/tasks/:taskId/results`,
        async (
            request: FastifyRequest<{ Params: { taskId: number }; Body: any }>,
            _
        ) => {
            const taskId = request.params.taskId;
            const jsonData = request.body;
            const results = await getTaskResults(taskId, jsonData);
            return results;
        }
    );

    app.post(
        `${apiBasePath}/tasks/:taskId/download`,
        async (
            request: FastifyRequest<{ Params: { taskId: number }; Body: any }>,
            reply
        ) => {
            const taskId = request.params.taskId;
            const jsonData = request.body;
            await downloadTaskResults(taskId, jsonData, reply as any);
        }
    );

    app.patch(
        `${apiBasePath}/tasks/:taskId/abort`,
        async (request: FastifyRequest<{ Params: { taskId: number } }>, _) => {
            const taskId = request.params.taskId;
            const result = await abortSingleTask(taskId);
            return result;
        }
    );

    app.delete(
        `${apiBasePath}/tasks/:taskId`,
        async (request: FastifyRequest<{ Params: { taskId: number } }>, _) => {
            const taskId = request.params.taskId;
            const result = await deleteSingleTask(taskId);
            return result;
        }
    );

    app.post(`${apiBasePath}/tasks/bulk-abort`, async (request, _) => {
        const jsonData = request.body;
        const result = await bulkAbortTasks(jsonData);
        return result;
    });

    app.post(`${apiBasePath}/tasks/bulk-delete`, async (request, _) => {
        const jsonData = request.body;
        const result = await bulkDeleteTasks(jsonData);
        return result;
    });

    app.get(`${apiBasePath}/ui/app-props`, getAppProps);

    app.post(
        `${apiBasePath}/ui/tasks/is-any-task-updated`,
        async (request, _) => {
            const jsonData = request.body;
            const result = await isAnyTaskUpdated(jsonData);
            return result;
        }
    );

    app.post(`${apiBasePath}/ui/tasks/is-task-updated`, async (request, _) => {
        const jsonData = request.body;
        const result = await isTaskUpdated(jsonData);
        return result;
    });

    app.get(`${apiBasePath}/ui/tasks`, async (request, _) => {
        const queryParams = request.query;
        const result = await getTasksForUiDisplay(queryParams);
        return result;
    });

    app.patch(`${apiBasePath}/ui/tasks`, async (request, _) => {
        const queryParams = request.query;
        const jsonData = request.body;
        const result = await patchTask(queryParams, jsonData);
        return result;
    });

    app.post(
        `${apiBasePath}/ui/tasks/:taskId/results`,
        async (
            request: FastifyRequest<{
                Params: { taskId: number };
                Body: any;
                Querystring: any;
            }>,
            _
        ) => {
            const taskId = request.params.taskId;
            const jsonData = request.body;
            const queryParams = request.query;
            const final = await getUiTaskResults(taskId, queryParams, jsonData);
            return final;
        }
    );

    // Add direct scraper routes for each scraper
    addScraperRoutes(app, apiBasePath);
    if (ApiConfig.routeSetupFn) {
        ApiConfig.routeSetupFn(app);
    }

    return app;
}
let server: FastifyInstance;
async function startServer(
    port: number,
    scrapers: any[],
    apiBasePath: string,
    routeAliases: any,
    enable_cache: boolean
): Promise<void> {
    try {
        if (server) {
            await stopServer();
        }
        server = buildApp(scrapers, apiBasePath, routeAliases, enable_cache);

        await server.listen({
            port,
            host: "0.0.0.0", // bind on all interfaces
        });
        console.log(
            `Server running on http://localhost:${port}${apiBasePath || "/"} 🟢`
        );
    } catch (err) {
        server = null as unknown as FastifyInstance;
        console.error(err);
        process.exit(1);
    }
}

async function stopServer(): Promise<void> {
    if (server) {
        try {
            // this way better as prevents multiple Server stopped calls
            const prev = server;
            server = null as unknown as FastifyInstance;
            await prev.close();
            console.log(`Server stopped 🔴`);
        } catch (err) {
            console.error(err);
            process.exit(1);
        }
    }
}

/**
 * Removes everything after (and including) the first single slash (/) in a string,
 * but skips over '//' (double slashes), which are used in protocols like 'http://'.
 * This is primarily used to extract the base URL (protocol + host) from a full URL.
 * 
 * Example:
 *   removeAfterFirstSlash("https://example.com/api/v1") // "https://example.com"
 *   removeAfterFirstSlash("http://foo/bar/baz") // "http://foo"
 *   removeAfterFirstSlash("localhost:8000/api/v1") // "localhost:8000"
 *   removeAfterFirstSlash("https://example.com") // "https://example.com"
 */
function removeAfterFirstSlash(inputString: string): string {
    let i = 0;
    const strLen = inputString.length;
    while (i < strLen) {
        const char = inputString[i];
        if (char === '/') {
            // Check for double slash (e.g., 'http://')
            if (i + 1 < strLen && inputString[i + 1] === '/') {
                i += 2;
                continue;
            } else {
                // Single slash: trim here
                return inputString.substring(0, i);
            }
        }
        i++;
    }
    // No single slash found (or only part of protocol), return the whole input
    return inputString;
}

/**
 * Configuration class for API.
 * Controls API-only mode, port settings, and autostart behavior.
 */
class ApiConfig {
    static apiPort: number = 8000;
    static autoStart: boolean = true;
    static routeSetupFn?: (server: FastifyInstance) => void;
    static apiBasePath: string = ""; // Default empty
    static routeAliases: Map<Function, string[]> = new Map();

    // Kubernetes configuration
    static nodeRole: NodeRole = 'standalone';

    /**
     * Enables API
     * @example
     * ApiConfig.enableApi();
     */
    static enableApi(): void {
        // @ts-ignore
        global.ApiConfig = ApiConfig;
        // @ts-ignore
        global.startServer = startServer;
        // @ts-ignore
        global.stopServer = stopServer;
    }



    /**
     * Enables Kubernetes Master-Worker mode.
     * 
     * This method configures the application for distributed task processing:
     * - If --master flag is passed: Acts as the master node (task distribution)
     * - If --worker flag is passed: Acts as a worker node (task execution)
     * - If neither flag is passed: Acts as normal desktop application (default behavior)
     * 
     * @param {string} masterEndpoint - The master node endpoint (e.g., "http://master-srv:3000")
     * @param {number | Record<string, number>} taskTimeout - Task timeout in seconds. Ideally set it to 2× your max expected task duration.
     *        Can be a single number (applies to all scrapers) or an object mapping scraper names/types to timeouts.
     *        Default: 8 hours (28800 seconds)
     * 
     * @example
     * // Simple usage with default timeout
     * ApiConfig.enableKubernetes("http://master-srv:3000");
     * 
     * @example
     * // Custom timeout for all scrapers
     * ApiConfig.enableKubernetes("http://master-srv:3000", 3600); // 1 hour
     * 
     * @example
     * // Different timeouts per scraper
     * ApiConfig.enableKubernetes("http://master-srv:3000", {
     *   "longRunningScraper": 14400,  // 4 hours
     *   "quickScraper": 1800          // 30 minutes
     * });
     */
    static async enableKubernetes({
        masterEndpoint,
        taskTimeout = DEFAULT_TASK_TIMEOUT
    }: {
        masterEndpoint: string,
        taskTimeout?: number | Record<string, number>
    }): Promise<void> {
        ApiConfig.enableApi()
        if (masterEndpoint) {
            masterEndpoint = removeAfterFirstSlash(masterEndpoint);
        }
        // Validate masterEndpoint
        if (!masterEndpoint || !isValidUrl(masterEndpoint)) {
            throw new Error(`Invalid masterEndpoint: "${masterEndpoint}". Must be a valid URL (e.g., "https://my-app.my-tunnel.app", "https://my-app.cloudflare-tunnel.app", "https://my-app.ngrok-free.app")`);
        }

        // Validate taskTimeout
        if (typeof taskTimeout === 'number') {
            if (taskTimeout < 60) {
                console.warn(`[K8s] Warning: taskTimeout (${taskTimeout}s) is less than 60 seconds. This may cause premature task reassignment.`);
            }
        }


        // Parse command line flags

        if (isMaster) {
            // Validate visibility timeout against scrapers if it's an object
            if (typeof taskTimeout === 'object') {
                Server.validateAgainstLimit(taskTimeout, 'task timeout');
            }

            // Set up master executor
            // @ts-ignore
            global.executor = new MasterExecutor(taskTimeout);
            this.nodeRole = 'master';
            console.log("[K8s] Starting as Kubernetes MASTER node 👑");

            // @ts-ignore
            global.master = true
            // Test self-connectivity (master calls itself)
            // @ts-ignore
            global.checkMasterHealth = () =>{
                setTimeout(async () => {
                    const result = await checkMasterHealth(masterEndpoint);
                    if (result) {
                        console.log("[K8s] Master health check passed ✓");
                    } else {
                        console.log("[K8s] Master health check failed ✗");
                    }
            }, 2000); // Delay to allow server to start
}
        } else if (isWorker) {
            // Set up worker executor
            // @ts-ignore
            global.executor = new WorkerExecutor(masterEndpoint);
            this.nodeRole = 'worker';
            console.log("[K8s] Starting as Kubernetes WORKER node 🔧");

            // Test master connectivity
            // @ts-ignore
            global.checkMasterHealth = () =>{
                setTimeout(async () => {
                    const result = await checkMasterHealth(masterEndpoint);
                    if (result) {
                        console.log("[K8s] Master health check passed ✓");
                    } else {
                        console.log("[K8s] Master health check failed ✗");
                    }
            }, 2000); // Delay to allow server to start
        }
        } else {
            // Standalone mode
            this.nodeRole = 'standalone';
            console.warn("[K8s] ⚠️  Running as standalone application.");
            console.warn("[K8s]    To run as master 👑: npm run k8s:master");
            console.warn("[K8s]    To run as worker 🔧: npm run k8s:worker");
        }
    }

    /**
     * Check if the current node is the master node.
     * @returns {boolean} true if running as master node
     */
    static isMasterNode(): boolean {
        return this.nodeRole === 'master';
    }

    /**
     * Check if the current node is a worker node.
     * @returns {boolean} true if running as worker node
     */
    static isWorkerNode(): boolean {
        return this.nodeRole === 'worker';
    }

    /**
     * Sets the port for the API server.
     * @param {number} [port=8000] - The port number to use
     * @example
     * ApiConfig.setApiPort(8080); // Uses port 8080
     * ApiConfig.setApiPort();      // Uses default port 8000
     */
    static setApiPort(port: number = 8000): void {
        this.apiPort = port;
    }

    /**
     * Disables automatic API server startup on application launch.
     * When enabled, API must be manually started from the API Tab in desktop GUI.
     * @example
     * ApiConfig.disableApiAutostart(); // API will not run until manually started from desktop GUI
     *
     */
    static disableApiAutostart(): void {
        this.autoStart = false;
    }

    /**
     * Sets the base path to be prefixed for all API routes.
     * Useful for mounting the API under a specific subpath like `/v1`.
     * @param {string} path - The base path to prefix (e.g., "/v1")
     * @example
     * ApiConfig.setApiBasePath("/v1"); // All routes will now be prefixed with /v1
     */
    static setApiBasePath(path: string): void {
        this.apiBasePath = cleanBasePath(path) as any;
    }

    /**
     * Adds an alias for a specific scraper's direct call route bypassing Task System.
     * @param {Function} scraper - The scraper function to add an alias for.
     * @param {string} endpoint - The alias path (e.g., '/hotels/search').
     * @example
     * ApiConfig.addScraperAlias(hotelsSearchScraper, '/hotels/search');
     */
    static addScraperAlias(scraper: Function, endpoint: string): void {
        if (!endpoint) return;

        if (!this.routeAliases.has(scraper)) {
            this.routeAliases.set(scraper, [cleanBasePath(endpoint)]);
        } else {
            const aliasArray = this.routeAliases.get(scraper)!;
            if (!aliasArray.includes(endpoint)) {
                aliasArray.push(cleanBasePath(endpoint));
            }
        }
    }

    /**
     * Adds custom routes to the API server using Fastify's routing system.
     *
     * The function receives a FastifyInstance object, which you can use to define your routes.
     *
     * When to use:
     * - Authentication middleware
     * - Custom data processing endpoints
     * - Adding Webhook receivers
     *
     * @param {(server: FastifyInstance) => void} routeSetupFn - Function that receives FastifyInstance to add custom routes
     * @example
     * // Adding a custom health check endpoint
     * ApiConfig.addCustomRoutes((server) => {
     *   server.get('/health', (request, reply) => {
     *     return reply.send({ status: 'OK'});
     *   });
     * });
     *
     * @example
     * // Adding a validation middleware
     * ApiConfig.addCustomRoutes((server) => {
     *   server.addHook('onRequest', (request, reply, done) => {
     *     // Check for secret
     *     const secret = request.headers['x-secret'] as string;
     *
     *     if (secret === '49cb1de3-419b-4647-bf06-22c9e1110313') {
     *       // Valid secret, proceed
     *       return done();
     *     } else {
     *       return reply.status(401).send({
     *         message: 'Unauthorized: Invalid secret.',
     *       });
     *     }
     *   });
     * });
     */
    static addCustomRoutes(
        routeSetupFn: (server: FastifyInstance) => void
    ): void {
        this.routeSetupFn = routeSetupFn;
    }
}
export default ApiConfig;