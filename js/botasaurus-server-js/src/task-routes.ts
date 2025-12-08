import { validateAndGetTaskId, validatePatchTask } from './validation';
import {
  executeAsyncTask,
  executeAsyncTasks,
  executeGetAppProps,
  executeGetTaskResults,
  executeGetTasks,
  executeGetUiTaskResults,
  executeGetUiTasks,
  executeIsAnyTaskFinished,
  executeIsTaskUpdated,
  executePatchTask,
  executeSyncTask,
  executeSyncTasks,
  executeTaskResults,
  getTaskFromDb,
  performPatchTask,
  OK_MESSAGE,
} from './routes-db-logic';
import { Server } from './server'

function home() {
  return { redirect: '/api' };
}

function getApi() {
  return OK_MESSAGE;
}

async function createAsyncTask(jsonData: any, withResult: boolean = true,giveFirstResultOnly: boolean = false,) {
  if (Array.isArray(jsonData)) {
    const result = await executeAsyncTasks(jsonData, withResult, giveFirstResultOnly);
    return result;
  } else {
    const result = await executeAsyncTask(jsonData, withResult, giveFirstResultOnly);
    return result;
  }
}

async function createSyncTask(jsonData: any) {
  if (Array.isArray(jsonData)) {
    const rst = await executeSyncTasks(jsonData);
    return rst;
  } else {
    const final = await executeSyncTask(jsonData);
    return final;
  }
}

async function getTasks(queryParams: any) {
  return await executeGetTasks(queryParams);
}

async function getTask(taskId: number) {
  return await getTaskFromDb(validateAndGetTaskId(taskId));
}

async function getTaskResults(taskId: number, jsonData: any) {
  const results = await executeGetTaskResults(validateAndGetTaskId(taskId), jsonData);
  return results;
}

async function downloadTaskResults(taskId: number, jsonData: any, reply=undefined) {
  return await executeTaskResults(validateAndGetTaskId(taskId), jsonData, reply);
}

async function abortSingleTask(taskId: number) {
  await performPatchTask('abort', validateAndGetTaskId(taskId));
  return OK_MESSAGE;
}

async function deleteSingleTask(taskId: number) {
  await performPatchTask('delete', validateAndGetTaskId(taskId));
  return OK_MESSAGE;
}

async function retrySingleTask(taskId: number) {
  await performPatchTask('retry', validateAndGetTaskId(taskId));
  return OK_MESSAGE;
}

async function bulkAbortTasks(jsonData: any) {
  const taskIds = validatePatchTask(jsonData);

  for (const taskId of taskIds) {
    await performPatchTask('abort', taskId);
  }

  return OK_MESSAGE;
}

async function bulkDeleteTasks(jsonData: any) {
  const taskIds = validatePatchTask(jsonData);

  for (const taskId of taskIds) {
    await performPatchTask('delete', taskId);
  }

  return OK_MESSAGE;
}

async function bulkRetryTasks(jsonData: any) {
  const taskIds = validatePatchTask(jsonData);

  for (const taskId of taskIds) {
    await performPatchTask('retry', taskId);
  }

  return OK_MESSAGE;
}

function getAppProps() {
  const result = executeGetAppProps();
  return result;
}

async function isAnyTaskUpdated(jsonData: any) {
  const result = await executeIsAnyTaskFinished(jsonData);
  return result;
}

async function isTaskUpdated(jsonData: any) {
  const result = await executeIsTaskUpdated(jsonData);
  return result;
}

async function getTasksForUiDisplay(queryParams: any) {
  const page = queryParams.page;
  const result = await executeGetUiTasks(page);
  return result;
}

async function patchTask(queryParams: any, jsonData: any) {
  const page = queryParams.page;
  const result = await executePatchTask(page, jsonData);
  return result;
}

async function getUiTaskResults(taskId: number, queryParams: any, jsonData: any, ) {
  const final = await executeGetUiTaskResults(validateAndGetTaskId(taskId), jsonData, queryParams);
  return final;
}

async function getSearchOptions(searchMethod: string, query: string, data: any) {
  try {
    
    // Check if the search method exists
    if (!Server.endpoints[searchMethod]) {
      return { error: `Search method '${searchMethod}' is not registered using Server.addSearchOptionsEndpoints().` };
    }

    // Call the search method
    const result = await Server.endpoints[searchMethod](query, data);

    // Validate the result is an array of objects with value and label
    if (!Array.isArray(result)) {
      return { error: `Search method '${searchMethod}' must return an array of objects.` };
    }

    for (const item of result) {
      if (typeof item !== 'object' || !item.hasOwnProperty('value') || !item.hasOwnProperty('label')) {
        return { error: `Each object in the result must have 'value' and 'label' properties.` };
      }
    }

    return result;
  } catch (error: any) {
    console.error(`Error in getSearchOptions for method '${searchMethod}':`, error);

    // Check if it's an Axios error
    if (error.isAxiosError || error.response) {
      const status = error.response?.status;
      const statusText = error.response?.statusText || 'Unknown error';
      
      if (status === 400) {
        return { error: `Bad Request: ${statusText}` };
      } else if (status === 404) {
        return { error: `Not Found: ${statusText}` };
      } else if (status === 500) {
        return { error: `Server Error: ${statusText}` };
      } else if (status) {
        return { error: `Request failed with status ${status}: ${statusText}` };
      }
    }

    // Generic error
    return { error: error.message || 'An unexpected error occurred while fetching search options.' };
  }
}

export {
  home,
  getApi,
  createAsyncTask,
  createSyncTask,
  getTasks,
  getTask,
  getTaskResults,
  downloadTaskResults,
  abortSingleTask,
  deleteSingleTask,
  retrySingleTask,
  bulkAbortTasks,
  bulkDeleteTasks,
  bulkRetryTasks,
  getAppProps,
  isAnyTaskUpdated,
  isTaskUpdated,
  getTasksForUiDisplay,
  patchTask,
  getUiTaskResults,
  getSearchOptions,
};