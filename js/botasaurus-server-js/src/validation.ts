import {  JsonHTTPResponseWithMessage } from './errors';
import { getScraperErrorMessage, Server } from './server';
import { isNotNullish, isNullish } from './null-utils';
import { isObject, isNotEmptyObject, parseBoolean } from './utils';


export function tryIntConversion(value: any, errorMessage: string): number {
    if (typeof value === 'string') {
        try {
            const parsed = parseInt(value, 10);
            if (!isNaN(parsed)) {
                return parsed;
            }
        } catch (error) {
            throw new JsonHTTPResponseWithMessage(errorMessage);
        }
        
    }else if (typeof value === 'number' && Number.isInteger(value) ){
        return value
    }
    throw new JsonHTTPResponseWithMessage(errorMessage);
}

export async function serialize(data: any, withResult: boolean = true){
    if (isNullish(data)) {
        return null;
    }
    if (Array.isArray(data)) {
        return Promise.all( data.map(item => item.toJson(withResult)));
    }
    return data.toJson(withResult);
}

export function createTaskNotFoundError(taskId: number): JsonHTTPResponseWithMessage {
    return new JsonHTTPResponseWithMessage(
        `Task ${taskId} not found`,
        404
    );
}

export function deepCloneDict(originalDict: any): any {
    if (!isObject(originalDict)) {
        return originalDict;
    }

    const newDict: { [key: string]: any } = {};
    for (const [key, value] of Object.entries(originalDict)) {
        if (isObject(value)) {
            newDict[key] = deepCloneDict(value);
        } else if (Array.isArray(value)) {
            newDict[key] = value.map(item => deepCloneDict(item));
        } else {
            newDict[key] = value;
        }
    }

    return newDict;
}

export function dictToString(errorsDict: { [key: string]: string[] }): string {
    const formattedPairs: string[] = [];
    for (const [key, values] of Object.entries(errorsDict)) {
        
        const valueStr = values.map(x => x.endsWith('.') ? x.slice(0, -1) : x).join('; ');
        const formattedPair = `${key}: ${valueStr}.`;
        formattedPairs.push(formattedPair);
    }

    const resultString = formattedPairs.join('\n');

    return resultString;
}

export function isStringOfMinLength(data: any, minLength = 1): boolean {
    return typeof data === 'string' && data.length >= minLength;
}


export function isStringOfAtLeast1Len(data: any): boolean {
    return typeof data === 'string' && data.length >= 1;
}

export const isValidId =  isValidPositiveInteger



export function ensureJsonBodyIsDict(jsonData: any): void {
    if (isNullish(jsonData)) {
        throw new JsonHTTPResponseWithMessage('json body must be provided');
    }

    if (!isObject(jsonData)) {
        throw new JsonHTTPResponseWithMessage('json body must be provided as an object');
    }
}

export function validateScraperName(scraperName: string | null): string {
    const validScraperNames = Server.getScrapersNames();
    const validNamesString = validScraperNames.join(', ');

    if (validScraperNames.length === 0) {
        const errorMessage = getScraperErrorMessage(validScraperNames, scraperName, validNamesString);
        throw new JsonHTTPResponseWithMessage(errorMessage);
    }

    if (isNullish(scraperName)) {
        if (validScraperNames.length === 1) {
            scraperName = validScraperNames[0];
        } else {
            const errorMessage = `'scraper_name' must be provided when there are multiple scrapers. The scraper_name must be one of ${validNamesString}.`;
            throw new JsonHTTPResponseWithMessage(errorMessage);
        }
    } else if (!Server.getScraper(scraperName!)) {
        const errorMessage = getScraperErrorMessage(validScraperNames, scraperName, validNamesString);

        throw new JsonHTTPResponseWithMessage(errorMessage);
    }
    return scraperName!;
}

export function validateTaskRequest(jsonData: any): [string, any, any, any] {
    ensureJsonBodyIsDict(jsonData);

    const scraperName = jsonData.scraper_name;
    const data = jsonData.data;

    const validatedScraperName = validateScraperName(scraperName);

    if (isNullish(data)) {
        throw new JsonHTTPResponseWithMessage("'data' key must be provided");
    }

    if (!isObject(data)) {
        throw new JsonHTTPResponseWithMessage("'data' key must be a valid JSON object");
    }

    const controls = Server.getControls(validatedScraperName);

    const result = controls.getBackendValidationResult(data);

    const errors = result.errors;

    if (isNotEmptyObject(errors)) {
        throw new JsonHTTPResponseWithMessage(dictToString(errors));
    }
    // use default if not provided
    let enableCache = jsonData.enable_cache ?? Server.cache;
    if (typeof enableCache !== 'boolean') {
        throw new JsonHTTPResponseWithMessage("'enable_cache' must be a boolean");
    }
    

    const validatedData = result.data;
    const metadata = result.metadata;
    return [validatedScraperName, validatedData, metadata, enableCache];
}



export function validateDirectCallRequest(scraperName:string, data:any): [any, any, boolean] {
    
    const controls = Server.getControls(scraperName);

    const result = controls.getBackendValidationResult(data, true);

    const errors = result.errors;

    if (isNotEmptyObject(errors)) {
        throw new JsonHTTPResponseWithMessage(dictToString(errors));
    }
    

    const validatedData = result.data;
    const metadata = result.metadata;

    const enableCache = parseBoolean(data.enable_cache) ?? Server.cache;
    return [validatedData, metadata, enableCache];
}

export function isValidPositiveInteger(param: any): boolean {
    return typeof param === 'number' && Number.isInteger(param) && param > 0;
}

export function isInteger(param: any): boolean {
    return typeof param === 'number' && Number.isInteger(param);
}

export function isValidPositiveIntegerIncludingZero(param: any): boolean {
    return typeof param === 'number' && Number.isInteger(param) && param >= 0;
}

export function validateFilters(jsonData: any): any {
    const filters = jsonData.filters;
    if (isNotNullish(filters)) {
        if (!isObject(filters)) {
            throw new JsonHTTPResponseWithMessage('Filters must be a dictionary');
        }
    }
    return filters;
}

export function validateView(jsonData: any, allowedViews: string[]): string | undefined {
    let view = jsonData.view;

    if (isNotNullish(view)) {
        if (!isStringOfMinLength(view)) {
            throw new JsonHTTPResponseWithMessage('View must be a string with at least one character');
        }

        view = view.toLowerCase();
        if (!allowedViews.includes(view)) {
            throw new JsonHTTPResponseWithMessage(`Invalid view. Must be one of: ${allowedViews.join(', ')}.`);
        }
    }

    return view;
}

export function validateSort(jsonData: any, allowedSorts: string[], defaultSort: string): string | null {
    let sort = jsonData.sort ?? defaultSort;

    if (sort === 'no_sort') {
        sort = null;
    } else if (isNotNullish(sort)) {
        if (!isStringOfMinLength(sort)) {
            throw new JsonHTTPResponseWithMessage('Sort must be a string with at least one character');
        }

        sort = sort.toLowerCase();
        if (!allowedSorts.includes(sort)) {
            throw new JsonHTTPResponseWithMessage(`Invalid sort. Must be one of: ${allowedSorts.join(', ')}.`);
        }
    } else {
        sort = defaultSort;
    }
    return sort;
}

export function validateResultsRequest(jsonData: any, allowedSorts: string[], allowedViews: string[], defaultSort: string): [any, string | null, string | undefined, number, number | undefined] {
    ensureJsonBodyIsDict(jsonData);

    const filters = validateFilters(jsonData);
    const sort = validateSort(jsonData, allowedSorts, defaultSort);
    const view = validateView(jsonData, allowedViews);

    let page = jsonData.page;
    if (isNotNullish(page)) {
        page = tryIntConversion(page, 'page must be an integer');

        // Now page is definitely an integer, just check range
        if (!isValidPositiveInteger(page)) {
            throw new JsonHTTPResponseWithMessage('page must be greater than or equal to 1');
        }
    } else {
        page = 1;
    }

    let per_page = jsonData.per_page;
    if (isNotNullish(per_page)) {
        per_page = tryIntConversion(per_page, 'per_page must be an integer');

        if (!isValidPositiveInteger(per_page)) {
            throw new JsonHTTPResponseWithMessage('per_page must be greater than or equal to 1');
        }
    } else {
        per_page = 25;
    }

    return [filters, sort, view, page, per_page];
}


export function validateDownloadParams(jsonData: any, allowedSorts: string[], allowedViews: string[], defaultSort: string): [string, any, string | null, string | undefined, boolean, string | null] {
    ensureJsonBodyIsDict(jsonData);

    let fmt = jsonData.format;

    if (isNullish(fmt)) {
        fmt = 'json';
    } else if (!isStringOfMinLength(fmt)) {
        throw new JsonHTTPResponseWithMessage('Format must be a string with at least one character');
    } else if (fmt === 'xlsx') {
        fmt = 'excel';
    }

    fmt = fmt.toLowerCase();
    if (!['json', 'csv', 'excel'].includes(fmt)) {
        throw new JsonHTTPResponseWithMessage('Invalid format. Must be one of: JSON, CSV, Excel');
    }

    const filters = validateFilters(jsonData);
    const sort = validateSort(jsonData, allowedSorts, defaultSort);
    const view = validateView(jsonData, allowedViews);

    let convertToEnglish = jsonData.convert_to_english ?? true;
    if (typeof convertToEnglish !== 'boolean') {
        throw new JsonHTTPResponseWithMessage('convert_to_english must be a boolean');
    }

    let downloadFolder = jsonData.downloadFolder;
    if (downloadFolder !== null && downloadFolder !== undefined && !isStringOfMinLength(downloadFolder)) {
        throw new JsonHTTPResponseWithMessage('downloadFolder must be a string or null');
    }

    return [fmt, filters, sort, view, convertToEnglish, downloadFolder];
}



export function isListOfValidIds(obj: any): boolean {
    return Array.isArray(obj) && obj.every(isValidId);
}

export function validateAndGetTaskId(id: any): number {
    if (isNullish(id)) {
        throw new JsonHTTPResponseWithMessage("Task id must be provided")        
    }
    
    if (isStringOfAtLeast1Len(id)) {
        const idStr = isObject(id) ? JSON.stringify(id) : id;
        id = tryIntConversion(id, `Task id '${idStr}' is invalid.`);
        
    }


    if (!isValidId(id)) {
        const idStr = isObject(id) ? JSON.stringify(id) : id;
        throw new JsonHTTPResponseWithMessage(`Task id '${idStr}' is invalid.`);
    }

    return id;
}


export function validatePatchTask(jsonData: any): number[] {
    ensureJsonBodyIsDict(jsonData);

    const taskIds = jsonData.task_ids;

    if (isNullish(taskIds)) {
        throw new JsonHTTPResponseWithMessage("'task_ids' must be provided");
    }

    if (!isListOfValidIds(taskIds)) {
        const taskIdsStr = isObject(taskIds) || Array.isArray(taskIds) ? JSON.stringify(taskIds) : taskIds;
        throw new JsonHTTPResponseWithMessage(`'task_ids' with value '${taskIdsStr}' must be a list of integers representing scraping task ids.`);
    }

    return taskIds;
}

export function validateUiPatchTask(jsonData: any): [string, number[]] {
    ensureJsonBodyIsDict(jsonData);

    let action = jsonData.action;
    const taskIds = jsonData.task_ids;

    if (isNullish(action)) {
        throw new JsonHTTPResponseWithMessage("'action' must be provided");
    }

    if (typeof action !== 'string') {
        throw new JsonHTTPResponseWithMessage("'action' must be a string");
    }
    action = action.toLowerCase();
    if (!['abort', 'delete'].includes(action)) {
        throw new JsonHTTPResponseWithMessage('\'action\' must be either "abort" or "delete"');
    }

    if (isNullish(taskIds)) {
        throw new JsonHTTPResponseWithMessage("'task_ids' must be provided. Task IDs are unique identifiers for scraping tasks.");
    }

    if (!isListOfValidIds(taskIds)) {
        const taskIdsStr = isObject(taskIds) || Array.isArray(taskIds) ? JSON.stringify(taskIds) : taskIds;
        throw new JsonHTTPResponseWithMessage(`'task_ids' with value '${taskIdsStr}' must be a list of integers representing scraping tasks.`);
    }

    return [action, taskIds];
}