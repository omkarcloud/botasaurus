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
import { executor } from "./executor"
import { Server } from "./server"
import { kebabCase } from 'change-case';
import { validateDirectCallRequest } from "./validation"
import { sleep } from 'botasaurus/utils'
import { DirectCallCacheService } from "./task-results"
import { isNotEmptyObject } from "./utils"
import { isDontCache } from "botasaurus/dontcache"
import { JsonHTTPResponseWithMessage } from "./errors"

function addCorsHeaders(reply: any) {
    reply.header("Access-Control-Allow-Origin", "*");
    reply.header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS");
    reply.header("Access-Control-Allow-Headers", "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token");
}

function sendJson(reply: any, result: any) {
    return reply.type("application/json").send(result);
}
function addScraperRoutes(app:FastifyInstance) {
    Object.values(Server.scrapers).forEach(scraper => {
        const routePath = `/${kebabCase(scraper.scraper_name)}`
        const fn = scraper.function
        const key = Server.isScraperBasedRateLimit ? scraper.scraper_name : scraper.scraper_type

        app.get(routePath, async (request, reply) => {
            try {
                const params: Record<string, any> = {};
                for (const [key, value] of Object.entries(request.query as any)) {
                    if (key.endsWith("[]")) {
                        params[key.slice(0, -2)] = value;
                    } else {
                        params[key] = value;
                    }
                }
                
                
                // Validate params against scraper's input definition
                const [validatedData, metadata] = validateDirectCallRequest(scraper.scraper_name, params)

                let cacheKey: string | undefined
                if (Server.cache) {
                    // Check cache
                    cacheKey = DirectCallCacheService.createCacheKey(scraper.scraper_name, validatedData)

                    if (DirectCallCacheService.has(cacheKey)) {
                        try {
                            const cachedResult = DirectCallCacheService.get(cacheKey)
                            return sendJson(reply, cachedResult ?? { result: null })
                        } catch (error) {
                            console.error(error)
                            // Continue with normal execution if cache fails
                        }
                    }
                }

                // Wait for capacity if needed
                while (!executor.hasCapacity(key)) {
                    await sleep(0.1)
                }

                // Execute scraper
                executor.incrementCapacity(key)
                const mt = isNotEmptyObject(metadata) ? { metadata } : {}
                try {
                    const results = await fn(validatedData, {
                        ...mt,
                        parallel: null,
                        cache: false,
                        beep: false,
                        raiseException: true,
                        closeOnCrash: true,
                        output: null,
                        createErrorLogs: false,
                        returnDontCacheAsIs: true,
                    })

                    let isResultDontCached = false
                    let finalResults = results

                    // Handle don't cache flag
                    if (isDontCache(results)) {
                        isResultDontCached = true
                        finalResults = results.data
                    }


                    // Cache results if appropriate
                    if (Server.cache && !isResultDontCached) {
                        try {
                            // @ts-ignore
                            DirectCallCacheService.put(cacheKey, finalResults)
                        } catch (cacheError) {
                            console.error('Cache storage error:', cacheError)
                            // Continue even if caching fails
                        }
                    }

                    return sendJson(reply, finalResults ?? { result: null })
                } finally {
                    executor.decrementCapacity(key)
                }
            } catch (error: any) {
                if (error instanceof JsonHTTPResponseWithMessage) {
                    throw error; // Re-throw the error to be handled elsewhere
                }        
                console.error('Scraping failed:', error)
                return reply.status(500).send({
                    error: 'Scraping failed',
                    message: error.message
                })
            }
        })
    })
}

export function buildApp(scrapers:any[]): FastifyInstance {
    const app = fastify({logger: true});

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
            reply
                .code(error.status)
                .headers(error.headers)
                .send(error.body);
        } else {
            console.error(error);
            // Default error handling
            reply.status(500).send({
                message: error.message || 'Internal Server Error'
            });
        }
    });
        
    // Routes
    app.get("/", (_, reply) => {
        const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><link rel="icon" href="https://botasaurus-api.omkar.cloud/favicon.ico"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#000000"><meta name="description" content="API documentation for using web scrapers"><link rel="apple-touch-icon" href="https://botasaurus-api.omkar.cloud/logo192.png"><title>Api Docs</title><script>window.scrapers=${JSON.stringify(scrapers)}</script>
<script defer="defer" src="https://botasaurus-api.omkar.cloud/static/js/main.b9312db8.js"></script>
<link href="https://botasaurus-api.omkar.cloud/static/css/main.69260e80.css" rel="stylesheet">
</head><body><noscript>You need to enable JavaScript to run this app.</noscript><div id="root"></div>`;
    
      return reply.type('text/html').send(html);
    });

    app.post("/tasks/create-task-async", async (request, reply) => {
        const jsonData = request.body;
        const result = await createAsyncTask(jsonData);
        return sendJson(reply, result);
    });

    app.post("/tasks/create-task-sync", async (request, reply) => {
        const jsonData = request.body;
        const result = await createSyncTask(jsonData);
        return sendJson(reply, result);
    });

    app.get("/tasks", async (request, reply) => {
        const queryParams = request.query;
        const result = await getTasks(queryParams);
        return sendJson(reply, result);
    });

    app.get(
        "/tasks/:taskId",
        async (
            request: FastifyRequest<{ Params: { taskId: number } }>,
            reply
        ) => {
            const taskId = request.params.taskId;
            const result = await getTask(taskId);
            return sendJson(reply, result);
        }
    );

    app.post(
        "/tasks/:taskId/results",
        async (
            request: FastifyRequest<{ Params: { taskId: number }; Body: any }>,
            reply
        ) => {
            const taskId = request.params.taskId;
            const jsonData = request.body;
            const results = await getTaskResults(taskId, jsonData);
            return sendJson(reply, results);
        }
    );

    app.post(
        "/tasks/:taskId/download",
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
        "/tasks/:taskId/abort",
        async (
            request: FastifyRequest<{ Params: { taskId: number } }>,
            reply
        ) => {
            
            const taskId = request.params.taskId;
            const result = await abortSingleTask(taskId);
            return sendJson(reply, result);
        }
    );

    app.delete(
        "/tasks/:taskId",
        async (
            request: FastifyRequest<{ Params: { taskId: number } }>,
            reply
        ) => {
            const taskId = request.params.taskId;
            const result = await deleteSingleTask(taskId);
            return sendJson(reply, result);
        }
    );

    app.post("/tasks/bulk-abort", async (request, reply) => {
        const jsonData = request.body;
        const result = await bulkAbortTasks(jsonData);
        return sendJson(reply, result);
    });

    app.post("/tasks/bulk-delete", async (request, reply) => {
        const jsonData = request.body;
        const result = await bulkDeleteTasks(jsonData);
        return sendJson(reply, result);
    });

    app.get("/ui/app-props", (_, reply) => {
        const result = getAppProps();
        return sendJson(reply, result);
    });

    app.post("/ui/tasks/is-any-task-updated", async (request, reply) => {
        const jsonData = request.body;
        const result = await isAnyTaskUpdated(jsonData);
        return sendJson(reply, result);
    });

    app.post("/ui/tasks/is-task-updated", async (request, reply) => {
        const jsonData = request.body;
        const result = await isTaskUpdated(jsonData);
        return sendJson(reply, result);
    });

    app.get("/ui/tasks", async (request, reply) => {
        const queryParams = request.query;
        const result = await getTasksForUiDisplay(queryParams);
        return sendJson(reply, result);
    });

    app.patch("/ui/tasks", async (request, reply) => {
        const queryParams = request.query;
        const jsonData = request.body;
        const result = await patchTask(queryParams, jsonData);
        return sendJson(reply, result);
    });

    app.post(
        "/ui/tasks/:taskId/results",
        async (
            request: FastifyRequest<{
                Params: { taskId: number };
                Body: any;
                Querystring: any;
            }>,
            reply
        ) => {
            const taskId = request.params.taskId;
            const jsonData = request.body;
            const queryParams = request.query;
            const final = await getUiTaskResults(taskId, queryParams, jsonData);
            return sendJson(reply, final);
        }
    );



    // Add direct scraper routes for each scraper
    addScraperRoutes(app)
    if (ApiConfig.routeSetupFn) {
        ApiConfig.routeSetupFn(app);
    }


    return app;
}
let server: FastifyInstance;
async function startServer(port:number, scrapers:any[]): Promise<void> {
        try {
            if (server) {
                await stopServer()
            }
            server = buildApp(scrapers);
            
            await server.listen({port, 
                host: '0.0.0.0' // bind on all interfaces
    
            });
            console.log(`Server running on http://127.0.0.1:${port}/ 🟢`);
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
            const prev = server
            server = null as unknown as FastifyInstance;
            await prev.close()
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
    static apiOnlyMode: boolean = false;
    static routeSetupFn?: (server: FastifyInstance) => void;

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
   * Runs the application in API-only mode (disables desktop GUI interface).
   * Useful for headless/server environments where GUI is not needed.
   * @example
   * ApiConfig.onlyStartApi(); // Runs only the API server
   */
    static onlyStartApi(): void {
        this.apiOnlyMode = true;
    }


    /**
     * Adds custom routes to the API server
     * @param {(server: FastifyInstance) => void} routeSetupFn - Function that receives FastifyInstance to add custom routes
     * @example
     * ApiConfig.addCustomRoutes((server) => {
     *   server.get('/custom', (_, reply) => reply.send({ custom: 'route' }));
     * });
     */
    static addCustomRoutes(routeSetupFn: (server: FastifyInstance) => void): void {
        this.routeSetupFn = routeSetupFn;
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
   * Sets the port for the API server.
   * @param {number} [port=8000] - The port number to use
   * @example
   * ApiConfig.setApiPort(8080); // Uses port 8080
   * ApiConfig.setApiPort();      // Uses default port 8000
   */
    static setApiPort(port: number = 8000): void {
        this.apiPort = port;
    }

}

export default ApiConfig ;