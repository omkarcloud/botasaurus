import axios, { AxiosResponse } from "axios";
import {
    getFilenameFromResponseHeaders,
    writeJsonResponse,
    writeFileResponse,
    removeAfterFirstSlash,
} from "./utils";

export class ApiException extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ApiException";
    }
}

function _createFilename(path: string): string {
    return "output/responses/" + path + ".json";
}

function raiseIfBadException(response: AxiosResponse): void {
    if (400 <= response.status && response.status < 500) {
        const data = response.data;
        const message = data?.message;
        if (message) {
            throw new ApiException(message);
        }
    }
}

export interface Task {
    id: number;
    status: "pending" | "in_progress" | "completed" | "failed" | "aborted";
    task_name: string;
    scraper_name: string;
    scraper_type: string;
    is_all_task: boolean;
    is_sync: boolean;
    is_large: boolean;
    parent_task_id: number | null;
    duration: number | null;
    started_at: string | null;
    finished_at: string | null;
    data: Record<string, any>;
    metadata: Record<string, any>;
    result: any;
    result_count: number;
    created_at: string;
    updated_at: string;
}


export interface PaginatedResponse<T> {
    count: number;
    total_pages: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface OkResponse {
    message: "OK";
}

// Helper to normalize path similar to Python's os.path.normpath
function normalizePath(path: string): string {
  return path
    .split("/")
    .filter(Boolean)
    .join("/")
    .replace(/\/+/g, "/");
}
function cleanBasePath(apiBasePath: string | null | undefined){
  
  if (typeof apiBasePath === "string") {
    let path = apiBasePath ? normalizePath(apiBasePath) : "";

    if (path === ".") {
      path = "";
    } else if (path) {
      if (!path.startsWith("/")) {
        path = "/" + path;
      }
      if (path.endsWith("/")) {
        path = path.slice(0, -1);
      }
    }

    return path;
  }
  return ''

}
/**
 * Configuration options for the Api client
 */
export interface ApiConfig {
    /** The base URL for the API server. If not specified, defaults to "http://localhost:8000". */
    apiUrl?: string;
    /** Indicates if the client should create response files for each API call. Useful for debugging. Defaults to true. */
    createResponseFiles?: boolean;
    /** Base path to prefix API endpoints (e.g., "/v1"). */
    apiBasePath?: string;
    /** Enable or disable caching for all requests. Overrides the server's cache setting. */
    enableCache?: boolean;
}

export default class Api {
    private _apiUrl: string;
    private _apiBasePath: string;
    private _createResponseFiles: boolean;
    private _enableCache: boolean | undefined;
    private readonly DEFAULT_API_URL = "http://localhost:8000";

    constructor({ 
        apiUrl, 
        createResponseFiles = false, 
        apiBasePath = "",
        enableCache
    }: ApiConfig = { createResponseFiles: true }) {
        /**
         * Initializes the API client with a specified server URL, base path, caching options, and an option to create response files.
         *
         * @param apiUrl The base URL for the API server. If not specified, defaults to "http://localhost:8000".
         * @param createResponseFiles Indicates if the client should create response files for each API call. This is useful for debugging or development purposes. Defaults to true.
         * @param apiBasePath Base path to prefix API endpoints (e.g., "/v1").
         * @param enableCache Enable or disable caching for all API requests. Overrides the server's cache setting.
         */
        this._apiUrl = apiUrl
            ? removeAfterFirstSlash(apiUrl)
            : this.DEFAULT_API_URL;
        this._createResponseFiles = createResponseFiles;
        this._apiBasePath = cleanBasePath(apiBasePath) as any;
        this._enableCache = enableCache;

        // Check if API is running (note: this is synchronous in the original, but should be async in TS)
        this.isApiRunning().then((isRunning) => {
            if (!isRunning) {
                throw new ApiException(
                    `API at ${this._apiUrl}${this._apiBasePath} is not running. Please check if the API is up and running.`
                );
            }
        });
    }

    private _writeJson(filename: string, data: any): void {
        /**
         * Writes data to a JSON file specified by the filename. This method only runs if the createResponseFiles flag is True.
         *
         * @param filename The filename for the JSON file to be created.
         * @param data The data to be written to the file.
         */
        if (this._createResponseFiles) {
            const path = _createFilename(filename);
            writeJsonResponse(path, data);
            console.log(`View ${filename} response at: ./${path}`);
        }
    }

    private _makeApiUrl(path: string): string {
        return `${this._apiUrl}${this._apiBasePath}${path === '' && this._apiBasePath? "":"/"}${path}`;
    }

    private _getCacheParams(): { enable_cache: boolean } | {} {
        return typeof this._enableCache === 'boolean' ? { enable_cache: this._enableCache } : {};
    }

    async isApiRunning(): Promise<boolean> {
        /**
         * Checks if the API is running by performing a health check on the "/api" endpoint.
         *
         * @return True if the health check is successful, otherwise False.
         */
        try {
            const response = await axios.get(this._makeApiUrl(""));
            return response.status === 200;
        } catch (error) {
            if (axios.isAxiosError(error) && error.code === "ECONNREFUSED") {
                throw new ApiException(`API at ${this._apiUrl}${this._apiBasePath} is not running. 
Check the network connection, or verify if the API is running on a different endpoint. In case the API is running on a different endpoint, you can pass the endpoint as follows:
const api = new Api({ apiUrl: 'https://example.com' })`);
            }
            throw error;
        }
    }

    async createAsyncTask({ data, scraperName }: { data: any; scraperName?: string }): Promise<Task> {
        /**
         * Submits an asynchronous task to the server.
         *
         * @param data The data to be received by the scraper.
         * @param scraperName The name of the scraper to use for the task. If not provided, the server will use the default scraper.
         * @return The created task object.
         */
        const url = this._makeApiUrl("tasks/create-task-async");
        const payload = {
            data,
            scraper_name: scraperName,
            ...this._getCacheParams(),
        };
        try {
            const response = await axios.post(url, payload);

            this._writeJson("create_async_task", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async createSyncTask({ data, scraperName }: { data: any; scraperName?: string }): Promise<Task> {
        /**
         * Submits a synchronous task to the server.
         *
         * @param data The data to be received by the scraper.
         * @param scraperName The name of the scraper to use for the task. If not provided, the server will use the default scraper.
         * @return The created task object.
         */
        const url = this._makeApiUrl("tasks/create-task-sync");
        const payload = {
            data,
            scraper_name: scraperName,
            ...this._getCacheParams(),
        };
        try {
            const response = await axios.post(url, payload);

            this._writeJson("create_sync_task", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async createAsyncTasks({ dataItems, scraperName }: { dataItems: any[]; scraperName?: string }): Promise<Task[]> {
        /**
         * Submits multiple asynchronous tasks to the server in a batch.
         *
         * @param dataItems A list of data items to be processed by the scraper.
         * @param scraperName The name of the scraper to use for the tasks. If not provided, the server will use the default scraper.
         * @return A list of created task objects.
         */
        const url = this._makeApiUrl("tasks/create-task-async");
        const payload = dataItems.map((data) => ({ 
            data, 
            scraper_name: scraperName,
            ...this._getCacheParams()
        }));
        try {
            const response = await axios.post(url, payload);

            this._writeJson("create_async_tasks", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async createSyncTasks({ dataItems, scraperName }: { dataItems: any[]; scraperName?: string }): Promise<Task[]> {
        /**
         * Submits multiple synchronous tasks to the server in a batch and waits for the results.
         *
         * @param dataItems A list of data items to be processed by the scraper.
         * @param scraperName The name of the scraper to use for the tasks. If not provided, the server will use the default scraper.
         * @return A list of created task objects, each with its processing result.
         */
        const url = this._makeApiUrl("tasks/create-task-sync");
        const payload = dataItems.map((data) => ({ 
            data, 
            scraper_name: scraperName,
            ...this._getCacheParams()
        }));
        try {
            const response = await axios.post(url, payload);

            this._writeJson("create_sync_tasks", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async getTasks({ page = 1, perPage, withResults = true }: { page?: number; perPage?: number; withResults?: boolean } = { page: 1, withResults: true }): Promise<PaginatedResponse<Task>> {
        /**
         * Fetches tasks from the server, with optional result inclusion, pagination, and filtering.
         *
         * @param page The page number for pagination.
         * @param perPage The number of tasks to return per page.
         * @param withResults Whether to include the task results in the response.
         * @return A dictionary containing the task results and pagination information.
         */
        const url = this._makeApiUrl("tasks");
        const params: any = {
            with_results: withResults,
        };
        if (page !== undefined && page !== null) params.page = page;
        if (perPage !== undefined && perPage !== null) params.per_page = perPage;
        try {
            const response = await axios.get(url, { params });

            if (this._createResponseFiles) {
                const hasManyPages = response.data.total_pages > 1;
                const filename = hasManyPages
                    ? `get_tasks-page-${page}`
                    : "get_tasks";
                const msg = hasManyPages
                    ? `get_tasks, page ${page}`
                    : "get_tasks";
                const path = _createFilename(filename);
                writeJsonResponse(path, response.data);
                console.log(`View ${msg} response at: ./${path}`);
            }

            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async getTask(taskId: number): Promise<Task> {
        /**
         * Retrieves a specific task by ID.
         *
         * @param taskId The ID of the task to retrieve.
         * @return The task object.
         */
        const url = this._makeApiUrl(`tasks/${taskId}`);
        try {
            const response = await axios.get(url);

            this._writeJson("get_task", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async getTaskResults({ taskId, filters, sort, view, page = 1, perPage }: { taskId: number; filters?: any; sort?: any; view?: any; page?: number; perPage?: number }): Promise<PaginatedResponse<Record<string, any>>> {
        /**
         * Retrieves the results of a specific task.
         *
         * @param taskId The ID of the task.
         * @param filters A dictionary of filters to apply to the task results, optional.
         * @param sort The sort to apply to the task results, optional.
         * @param view The view to apply to the task results, optional.
         * @param page The page number to retrieve, default is 1.
         * @param perPage The number of results to return per page. If perPage is not provided, all results are returned, optional.
         * @return A dictionary containing the task results and pagination information if page and perPage are provided.
         */
        const url = this._makeApiUrl(`tasks/${taskId}/results`);
        const payload: any = { page };
        if (filters) payload.filters = filters;
        if (sort) payload.sort = sort;
        if (view) payload.view = view;
        if (perPage) payload.per_page = perPage;

        try {
            const response = await axios.post(url, payload);

            if (this._createResponseFiles) {
                const hasManyPages = response.data.total_pages > 1;
                const filename = hasManyPages
                    ? `get_task_results-page-${page}`
                    : "get_task_results";
                const msg = hasManyPages
                    ? `get_task_results, page ${page}`
                    : "get_task_results";
                const path = _createFilename(filename);
                writeJsonResponse(path, response.data);
                console.log(`View ${msg} response at: ./${path}`);
            }

            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async get(scraperName: string, data: Record<string, any>): Promise<any> {
        /**
         * Makes a direct GET request to the scraper endpoint, bypassing the task creating and scheduling system.
         *
         * @param scraperName The name of the scraper, which corresponds to the route path (e.g., "scrape-heading-task").
         * @param data The data to be received by the scraper.
         * @return The result from the scraper.
         */

        if (scraperName.startsWith('/')) {
            scraperName = scraperName.slice(1);
        }
        const url = this._makeApiUrl(scraperName);
        const params = {
            ...data,
            ...this._getCacheParams()
        };
        try {
            const response = await axios.get(url, { params });
            const fileScraperName = scraperName.replaceAll('/', '-');
            this._writeJson(`${fileScraperName}-result`, response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }


    async downloadTaskResults({ taskId, format, filters, sort, view, convertToEnglish = true }: { taskId: number; format?: string; filters?: any; sort?: any; view?: any; convertToEnglish?: boolean }): Promise<{
        buffer: Buffer;
        filename: string;
    }> {
        /**
         * Downloads the results of a specific task in the specified format.
         *
         * @param taskId The ID of the task.
         * @param format The format to download the task results in. Available formats are "json", "csv", "excel". The default format is "json".
         * @param filters A dictionary of filters to apply to the task results, optional.
         * @param sort The sort to apply to the task results, optional.
         * @param view The view to apply to the task results, optional.
         * @param convertToEnglish Whether to convert the task results to English, default is True, optional.
         * @return A tuple containing the downloaded content as a buffer and the filename.
         */
        const url = this._makeApiUrl(`tasks/${taskId}/download`);
        const payload: any = { convert_to_english: convertToEnglish };
        if (format) payload.format = format;
        if (filters) payload.filters = filters;
        if (sort) payload.sort = sort;
        if (view) payload.view = view;

        try {
            const response = await axios.post(url, payload, {
                responseType: "arraybuffer",
            });

            let buffer: Buffer;
            try {
                buffer = Buffer.from(response.data, 'utf8');
            } catch (bufferError) {
                throw new ApiException("Failed to create buffer from response data. Ensure the response data is valid.");
            }
            // @ts-ignore
            const filename = getFilenameFromResponseHeaders(response);

            if (this._createResponseFiles) {
                const path = writeFileResponse(
                    "output/responses/",
                    filename,
                    buffer
                );
                console.log(`View downloaded file at: ./${path}`);
            }

            return { buffer, filename };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async abortTask(taskId: number): Promise<OkResponse> {
        /**
         * Aborts a specific task.
         *
         * @param taskId The ID of the task to abort.
         * @return A success message.
         */
        const url = this._makeApiUrl(`tasks/${taskId}/abort`);
        try {
            const response = await axios.patch(url, {}, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            this._writeJson("abort_task", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async deleteTask(taskId: number): Promise<OkResponse> {
        /**
         * Deletes a specific task.
         *
         * @param taskId The ID of the task to delete.
         * @return A success message.
         */
        const url = this._makeApiUrl(`tasks/${taskId}`);
        try {
            const response = await axios.delete(url);

            this._writeJson("delete_task", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async deleteTasks({ taskIds }: { taskIds: number[] }): Promise<OkResponse> {
        /**
         * Bulk deletes tasks.
         *
         * @param taskIds A list of task IDs to be deleted.
         * @return A success message.
         */
        const url = this._makeApiUrl("tasks/bulk-delete");
        const payload = { task_ids: taskIds };
        try {
            const response = await axios.post(url, payload);

            this._writeJson("delete_tasks", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }

    async abortTasks({ taskIds }: { taskIds: number[] }): Promise<OkResponse> {
        /**
         * Bulk aborts tasks.
         *
         * @param taskIds A list of task IDs to be aborted.
         * @return A success message.
         */
        const url = this._makeApiUrl("tasks/bulk-abort");
        const payload = { task_ids: taskIds };
        try {
            const response = await axios.post(url, payload);

            this._writeJson("abort_tasks", response.data);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                raiseIfBadException(error.response as AxiosResponse);
            }
            throw error;
        }
    }
}