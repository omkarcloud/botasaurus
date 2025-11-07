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
import { executor } from "./executor";
import { Server } from "./server";
import { kebabCase } from "change-case";
import { validateDirectCallRequest } from "./validation";
import { sleep } from "botasaurus/utils";
import { DirectCallCacheService } from "./task-results";
import { cleanBasePath, isNotEmptyObject, isObject } from "./utils";
import { isDontCache } from "botasaurus/dontcache";
import { JsonHTTPResponseWithMessage } from "./errors";
import { cleanDataInPlace } from "botasaurus/output";
import { removeDuplicatesByKey } from "./models";

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
                    dataItems = splitTask(validatedData);
                } else {
                    dataItems = [validatedData];
                }

                const mt = isNotEmptyObject(metadata) ? { metadata } : {};
                let shouldDecrementCapacity = false;

                function restoreCapacity() {
                    if (shouldDecrementCapacity) {
                        executor.decrementCapacity(key);
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
                                while (!executor.hasCapacity(key)) {
                                    await sleep(0.1);
                                }
                                executor.incrementCapacity(key);
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
export function buildApp(
    scrapers: any[],
    apiBasePath: string,
    routeAliases: any,
    enable_cache: boolean
): FastifyInstance {
    const app = fastify({ logger: true });

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
    app.setErrorHandler((error, _, reply) => {
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

    // Routes
    app.get(apiBasePath || "/", (_, reply) => {
        const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><link rel="icon" href="https://botasaurus-api.omkar.cloud/favicon.ico"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#000000"><meta name="description" content="API documentation for using web scrapers"><link rel="apple-touch-icon" href="https://botasaurus-api.omkar.cloud/logo192.png"><title>Api Docs</title><script>window.enable_cache=${enable_cache};window.scrapers=${JSON.stringify(
            scrapers
        )};window.apiBasePath="${
            apiBasePath || ""
        }";window.routeAliases=${JSON.stringify(
            routeAliases
        )};</script><script defer="defer" src="https://botasaurus-api.omkar.cloud/static/js/main.5d995feb.js"></script><link href="https://botasaurus-api.omkar.cloud/static/css/main.69260e80.css" rel="stylesheet"></head><body><noscript>You need to enable JavaScript to run this app.</noscript><div id="root"></div></body></html>`;

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
 * Configuration class for API.
 * Controls API-only mode, port settings, and autostart behavior.
 */
class ApiConfig {
    static apiPort: number = 8000;
    static autoStart: boolean = true;
    static routeSetupFn?: (server: FastifyInstance) => void;
    static apiBasePath: string = ""; // Default empty
    static routeAliases: Map<Function, string[]> = new Map();

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
