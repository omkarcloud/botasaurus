import fs from 'fs';
import { createTask, createTaskName, db, getAutoincrementId, isFailedAndNonAllTask, isoformat, serializeTask, serializeUiDisplayTask, serializeUiOutputTask, Task, TaskStatus } from './models';
import { isNotNullish, isNullish } from './null-utils';
import { isObject, isNotEmptyObject } from './utils';
import { kebabCase } from 'change-case';
import { deepCloneDict, isStringOfMinLength, serialize, validateScraperName, validateTaskRequest, validateResultsRequest, validateDownloadParams, isValidPositiveInteger, isValidPositiveIntegerIncludingZero,isListOfValidIds,  isValidId, validateUiPatchTask, createTaskNotFoundError, tryIntConversion } from './validation';
import { TaskHelper, createProjection } from './task-helper';
import { TaskResults, createCacheKey } from './task-results';
import { Server } from './server';
import { applyPagination, calculatePageEnd, calculatePageStart } from './apply-pagination';
import { applyFiltersInPlace } from './filters';
import { applySorts } from './sorts';
import { _applyViewForUi, _applyViewForUiLargeTask, findView, transformRecord, getFields } from './views';

// import { downloadResults } from './download';
// import { convertUnicodeDictToAsciiDict } from './convert-to-english';
import { executor } from './executor'
import { sleep } from 'botasaurus/utils'
import { JsonHTTPResponseWithMessage } from './errors'
import { convertUnicodeDictToAsciiDict } from './convert-to-english'
import { downloadResults, downloadResultsHttp } from './download'
import { getBotasaurusStorage } from 'botasaurus/botasaurus-storage'
import { Launcher } from 'chrome-launcher/dist/chrome-launcher';
import { electronConfig } from './paths'

// Wrap NeDB operations in promises since it uses callbacks
const wrapDbOperationInPromise = (operation: any): Promise<any> => {
  return new Promise((resolve, reject) => {
    operation((err: Error, result: any) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
};


async function performCreateAllTask(
  data: any,
  metadata: any,
  is_sync: boolean,
  scraper_name: string,
  scraper_type: string,
  all_task_sort_id: number,
  withResult: boolean = true
): Promise<[any, string]> {
  const allTask = new Task({
    id: await getAutoincrementId(),
    status: TaskStatus.PENDING,
    sort_id: all_task_sort_id,
    task_name: 'All Task',
    scraper_name,
    scraper_type,
    is_all_task: true,
    is_sync,
    is_large:false,
    parent_task_id: null,
    data,
    meta_data: metadata,
    started_at:null, 
    finished_at:null, 
    result_count:0,
  });

  return wrapDbOperationInPromise((cb:any) => db.insert(allTask, cb))
    .then(async (newDoc) => {
      return [await serialize(createTask(newDoc), withResult), newDoc.id]
    });
}


async function performCreateTasks(tasks: any[], cachedTasks?: any[], withResult: boolean = true, giveFirstResultOnly: boolean = false,): Promise<any> {
  return new Promise((resolve, reject) => {
    db.insert(tasks, async (err, newDocs) => {
      if (err) {
        reject(err);
      } else {
        if (cachedTasks) {
          const fileList:any = cachedTasks.map((t) => [t.id, t.__cache_key]);
          await parallelCreateFiles(fileList);
        }
        
        if (giveFirstResultOnly) {
          resolve(newDocs.slice(0, 1))
        }else {
        resolve(await serialize(newDocs.map(createTask), withResult));
        }
      }
    });
  });
}

async function performCompleteTask(all_task_id: number, removeDuplicatesBy: any): Promise<void> {
  await executor.completeAsMuchAllTaskAsPossible(all_task_id, removeDuplicatesBy);
}

async function isTaskDone(taskId: number): Promise<boolean> {
  return TaskHelper.isTaskCompletedOrFailed(taskId);
}

async function queryTasks(
  ets: string[],
  withResults: boolean,
  page?: any,
  per_page?: any,
  serializer: (task: any, withResults: boolean) => Promise<any> = serializeTask
): Promise<any> {
  const projectionFields = createProjection(ets);
  const total_count = await wrapDbOperationInPromise((cb:any) => db.count({}, cb));

  if (isNullish(per_page)) {
    per_page = total_count === 0 ? 1 : total_count;
    page = 1;
  } else {
    per_page = parseInt(per_page.toString(), 10);
  }

  const total_pages = Math.max(Math.ceil(total_count / per_page), 1);

  page = isNullish(page) ? 1 : Math.max(Math.min(page, total_pages), 1);

  const tasks = await wrapDbOperationInPromise((cb:any) => {
    let query = db.find({}).projection(projectionFields).sort({ sort_id: -1 });
    
    if (isNotNullish(per_page)) {
      const start = (page - 1) * per_page;
      query = query.skip(start).limit(per_page);
    }
    
    query.exec(cb);
  });

  const currentPage = isNullish(page) ? 1 : page;
  const nextPage = currentPage * per_page < total_count ? currentPage + 1 : null;
  const previousPage = currentPage > 1 ? currentPage - 1 : null;

  return {
    count: total_count,
    total_pages,
    next: nextPage ? createPageUrl(nextPage, per_page, withResults) : null,
    previous: previousPage ? createPageUrl(previousPage, per_page, withResults) : null,
    results: await Promise.all(tasks.map((task: any) => serializer(task, withResults))),
  };
}



async function getTaskFromDb(taskId: number): Promise<Task> {
    const task = await TaskHelper.getTask(taskId);
    if (task) { 
        return serialize(task);
    } else {
        throw createTaskNotFoundError(taskId);
    }
}


async function performIsAnyTaskFinished(
  pendingTaskIds: string[],
  progressTaskIds: string[],
  allTasks: any[]
): Promise<boolean> {
  const allTasksQuery = allTasks.map((x) => ({
    $and: [{ id: x.id }, { result_count: { $gt: x.result_count } }],
  }));

  return new Promise((resolve, reject) => {
    db.findOne(
      {
        $or: [
          { $and: [{ id: { $in: pendingTaskIds } }, { status: { $ne: TaskStatus.PENDING } }] },
          { $and: [{ id: { $in: progressTaskIds } }, { status: { $ne: TaskStatus.IN_PROGRESS } }] },
          ...allTasksQuery,
        ],
      },
      { id: 1 },
      (err, task) => {
        if (err) {
          reject(err);
        } else {
          resolve(!!task);
        }
      }
    );
  });
}

async function performIsTaskUpdated(taskId: number){
  return new Promise((resolve, reject) => {
    db.findOne(
      { id: taskId },
      { updated_at: 1, status: 1 },
      (err, task) => {
        if (err) {
          reject(err);
        } else if (task) {
          resolve([task.updated_at, task.status]);
        } else {
          resolve(null);
        }
      }
    );
  });
}

async function performDownloadTaskResults(taskId: number) {
  const task = await TaskHelper.getTaskWithEntities(taskId, [
    'scraper_name',
    'status',
    'is_all_task',
    'data',
    'is_large',
    'task_name',
  ]);

  if (isNotNullish(task)) {
    const scraper_name = task.scraper_name;
    const task_data = task.data;
    const is_all_task = task.is_all_task;
    const task_name = task.task_name;
    const is_large = task.is_large;
    const status = task.status;
    

    const results = is_large ? null :await TaskResults.getTask(taskId);

    return [scraper_name,status, results, task_data, is_all_task, is_large, task_name];
  } else {
    throw createTaskNotFoundError(taskId);
  }
}


async function performGetUiTaskResults(taskId: number){
  const task = await TaskHelper.getTaskWithEntities(taskId, [
    'scraper_name',
    'result_count',
    'data',
    'is_large',
    'updated_at',
    'status',
    'is_all_task',
  ]);

  if (isNullish(task)) {
    throw createTaskNotFoundError(taskId);
  }
  const scraper_name = task.scraper_name;
  const task_data = task.data;
  const result_count = task.result_count;
  const is_large = task.is_large;
  const is_all_task = task.is_all_task;
  const status = task.status;
  
  const serializedTask = serializeUiDisplayTask(task);

  return [scraper_name, is_all_task,  status, is_large, serializedTask, task_data, result_count];
}

async function performPatchTask(action: string, taskId: number): Promise<void> {
  const task = await new Promise<any>((resolve, reject) => {
    db.findOne(
      { id: taskId },
      { id:1, is_all_task: 1, parent_task_id: 1, scraper_name: 1 },
      (err, task) => {
        if (err) {
          reject(err);
        } else if (task) {
          resolve(task);
        } else {
          resolve(null);
        }
      }
    );
  });

  if (task) {
    const removeDuplicatesBy = Server.getRemoveDuplicatesBy(task.scraper_name);
    const { is_all_task, parent_task_id } = task;

    if (action === 'delete') {
      await deleteTask(taskId, is_all_task, parent_task_id, removeDuplicatesBy);
    } else if (action === 'abort') {
      await abortTask(taskId, is_all_task, parent_task_id, removeDuplicatesBy);
    }
  }
}

export const OK_MESSAGE = { message: 'OK' };

async function createAsyncTask(validatedData: [string, any, any, any], withResult: boolean = true, giveFirstResultOnly: boolean = false, ): Promise<any> {
  const [scraper_name, data, metadata, enable_cache] = validatedData;

  const [tasksWithAllTask, tasks, split_task] = await createTasks(
    Server.getScraper(scraper_name),
    data,
    metadata,
    enable_cache, 
    false,
    withResult, 
    giveFirstResultOnly,
  );

  if (split_task) {
    return tasksWithAllTask;
  } else {
    return tasks[0];
  }
}

async function executeAsyncTask(jsonData: any, withResult: boolean = true,giveFirstResultOnly: boolean = false, ): Promise<any> {
  const result = await createAsyncTask(validateTaskRequest(jsonData), withResult, giveFirstResultOnly);
  return result;
}

async function executeAsyncTasks(jsonData: any[], withResult: boolean = true, giveFirstResultOnly: boolean = false, ): Promise<any[]> {
  const validatedDataItems = jsonData.map(validateTaskRequest);
  const result = await Promise.all(
    validatedDataItems.map(data => createAsyncTask(data, withResult, giveFirstResultOnly))
  );
  return result;
}
function isChromeInstalled() {
  try {
    return !!Launcher.getFirstInstallation();
  } catch (error) {
    console.error("Error checking Chrome installation:", error);
    return false;
  }
}


function checkChrome() {
  if (!getBotasaurusStorage().getItem("isChromeInstalled", false)) {
      const installed = isChromeInstalled();
      getBotasaurusStorage().setItem("isChromeInstalled", installed);

      if (!installed) {
        throw new Error("GOOGLE_CHROME_REQUIRED");
      }
  }
}


async function createTasks(
  scraper: any,
  data: any,
  metadata: any,
  enable_cache:any, 
  is_sync: boolean,
  withResult: boolean = true, 
  giveFirstResultOnly: boolean = false, 
): Promise<[any[], any[], boolean]> {
  if (scraper.isGoogleChromeRequired) {
    checkChrome()    
  }
  const createAllTasks = scraper.create_all_task;
  const split_task = scraper.split_task;
  const scraper_name = scraper.scraper_name;
  const scraper_type = scraper.scraper_type;
  const get_task_name = scraper.get_task_name;

  // Makes space for 10000 Tasks, 1000ms * 100
  let all_task_sort_id = Date.now() * 100;
  let allTask = null;
  let all_task_id:any = null;

  let tasksData: any[];
  if (split_task) {
    tasksData = split_task(deepCloneDict(data));
    if (tasksData.length === 0) {
      return [[], [], split_task];
    }
  } else {
    tasksData = [data];
  }

  if (createAllTasks) {
    [allTask, all_task_id] = await performCreateAllTask(
      data,
      metadata,
      is_sync,
      scraper_name,
      scraper_type,
      all_task_sort_id,
      withResult,
    );
    const new_id = all_task_sort_id -1
    // make all task comes at the top
    all_task_sort_id = new_id
  }

  const buildTask =  (task_data: any, sort_id: number) => new Task({
    id: getAutoincrementId(),
    status: TaskStatus.PENDING,
    sort_id,
    task_name: get_task_name ? get_task_name(task_data) : null,
    scraper_name,
    scraper_type,
    is_all_task: false,
    is_sync,
    is_large:false,
    parent_task_id: all_task_id,
    started_at:null, 
    finished_at:null, 
    data: task_data,
    meta_data: metadata,
    result_count:0,
  });

  const createCachedTasks = async (task_datas: any[]) => {
    const ls = task_datas.map((t) => ({
      key: createCacheKey(scraper_name, t),
      task_data: t,
    }));
    const cacheKeys = ls.map((item) => item.key);

    const cacheSet = await createCacheDetails(cacheKeys);

    const tasks: any[] = [];
    const cachedTasks: any[] = [];

    const createCachedTask = async (task_data: any, cacheKey: any, sort_id: number) => {
      const now_time = new Date()
      const {count:cachedResultCount, isLarge} = await TaskResults.getCachedItemDetails(cacheKey)
      return new Task({
        id: getAutoincrementId(),
        status: TaskStatus.COMPLETED,
        sort_id,
        task_name: get_task_name ? get_task_name(task_data) : null,
        scraper_name,
        scraper_type,
        is_all_task: false,
        is_sync,
        is_large:isLarge,
        parent_task_id: all_task_id,
        started_at: now_time,
        finished_at: now_time,
        data: task_data,
        meta_data: metadata,
        result_count: cachedResultCount,
      })
    };

    for (let i = 0; i < ls.length; i++) {
      const item = ls[i];
      if (cacheSet.has(item.key)) {
        const sort_id = all_task_sort_id - (i + 1);
        const ts = await createCachedTask(item.task_data, item.key, sort_id);
        // @ts-ignore
        ts.__cache_key = item.key;
        tasks.push(ts);
        cachedTasks.push(ts);
      } else {
        const sort_id = all_task_sort_id - (i + 1);
        tasks.push(buildTask(item.task_data, sort_id));
      }
    }

    return [tasks, cachedTasks, cachedTasks.length];
  };

  let tasks: any[];
  let cachedTasks: any[];
  let cachedTasksLen: number;
  if (enable_cache) {
    [tasks, cachedTasks, cachedTasksLen] = (await createCachedTasks(tasksData)) as any;
    tasks = await performCreateTasks(tasks, cachedTasks, withResult, giveFirstResultOnly);
  } else {
    tasks = tasksData.map((task_data, idx) => {
      const sort_id = all_task_sort_id - (idx + 1);
      return buildTask(task_data, sort_id);
    });
    cachedTasksLen = 0;

    tasks = await performCreateTasks(tasks, undefined, withResult, giveFirstResultOnly);
  }

  if (cachedTasksLen > 0) {
    const tasklen = tasks.length;
    if (tasklen === cachedTasksLen) {
      if (all_task_id) {
        // @ts-ignore
        const firstStartedAt = cachedTasks[0].started_at;
        TaskHelper.updateTask(
          all_task_id, 
          { started_at: firstStartedAt, finished_at: firstStartedAt }
        )
        // @ts-ignore
        allTask.started_at = isoformat(firstStartedAt);
        // @ts-ignore
        allTask.finished_at = isoformat(firstStartedAt);
      }
      console.log('All Tasks Results are Returned from cache');
    } else {
      console.log(`${cachedTasksLen} out of ${tasklen} Results are Returned from cache`);
    }
    if (all_task_id) {
      await performCompleteTask(all_task_id, Server.getRemoveDuplicatesBy(scraper_name));
    }
  } 

  let tasksWithAllTask = tasks;
  if (all_task_id) {
    tasksWithAllTask = [allTask, ...tasks];
  }

  return [tasksWithAllTask, tasks, split_task];
}

async function save(x: [number, string]) {
  await TaskResults.cloneTaskFromCacheKey(x[0], x[1]);
}

 async function parallelCreateFiles(fileList: [number, string][]){
    return Promise.all(fileList.map(save));
  }
  
  async function createCacheDetails(cacheKeys: string[]) {
    return new Set(TaskResults.filterItemsInCache(cacheKeys))
  }
  
  async function refetchTasks(item: any | any[]): Promise<any> {
    if (Array.isArray(item)) {
      const ids = item.map((i) => i.id);
      const tasks = await TaskHelper.getTasksByIds(ids);
      return serialize(tasks);
    } else {
      const task = await TaskHelper.getTask(item.id);
      return serialize(task);
    }
    }
  
  async function executeSyncTask(jsonData: any): Promise<any> {
    const [scraper_name, data, metadata, enableCache]= validateTaskRequest(jsonData);
  
    const [tasksWithAllTask, tasks, split_task] = await createTasks(
      Server.getScraper(scraper_name),
      data,
      metadata,
      enableCache, 
      true
    );
  
    const waitTasks = tasksWithAllTask && tasksWithAllTask[0].is_all_task
      ? [tasksWithAllTask[0]]
      : tasks;
  
    for (const task of waitTasks) {
      const taskId = task.id;
      while (!(await isTaskDone(taskId))) {
        await sleep(0.1);
      }
    }
  
    const final = split_task
      ? await refetchTasks(tasksWithAllTask)
      : await refetchTasks(tasks[0]);
  
    return final;
  }
  
  async function executeSyncTasks(jsonData: any[]): Promise<any[]> {
    const validatedDataItems = jsonData.map(validateTaskRequest);
  
    const ts = await Promise.all(
      validatedDataItems.map(async (validatedDataItem) => {
        const [scraper_name, data, metadata, enableCache] = validatedDataItem;
        return createTasks(Server.getScraper(scraper_name), data, metadata, enableCache, true);
      })
    );
  
    for (const t of ts) {
      const [tasksWithAllTask, tasks, _] = t;
  
      const waitTasks = tasksWithAllTask && tasksWithAllTask[0].is_all_task
        ? [tasksWithAllTask[0]]
        : tasks;
  
      for (const task of waitTasks) {
        const taskId = task.id;
        while (!(await isTaskDone(taskId))) {
          await sleep(0.1);
        }
      }
    }
  
    const rst = await Promise.all(
      ts.map(async (t) => {
        const [tasksWithAllTask, tasks, split_task] = t;
        return split_task
          ? await refetchTasks(tasksWithAllTask)
          : await refetchTasks(tasks[0]);
      })
    );
  
    return rst;
  }
  
  function getEts(_: boolean): string[] {
    return [
      'id',
      'status',
      'task_name',
      'scraper_name',
      'result_count',
      'scraper_type',
      'is_all_task',
      'is_sync',
      'is_large',
      'parent_task_id',
      'data',
      'meta_data',
      'finished_at',
      'started_at',
      'created_at',
      'updated_at',
    ];
  }
  
  function createPageUrl(page: number, per_page: number, withResults: boolean) {
    const queryParams: Record<string, any> = {};
  
    if (page) {
      queryParams.page = page;
    }
  
    if (isNotNullish(per_page)) {
      queryParams.per_page = per_page;
    }
  
    if (!withResults) {
      queryParams.with_results = false;
    }
    if (isNotEmptyObject(queryParams)) {
      return queryParams;  
    }
    return null;
  }
  async function executeGetTasks(queryParams: Record<string, any>): Promise<any> {
    const withResults = (queryParams.with_results || 'true').toLowerCase() === 'true';
  
    let page = queryParams.page;
    let per_page = queryParams.per_page;
  
    if (isNotNullish(per_page)) {
      per_page = tryIntConversion(per_page, `Invalid 'per_page' parameter value: "${page}". It must be a positive integer.`);
      if (!isValidPositiveInteger(per_page)) {
        throw new JsonHTTPResponseWithMessage(
          `Invalid 'per_page' parameter value: "${page}". It must be a positive integer.`
        );
      }
    } else {
      page = 1;
      per_page = null;
    }
  
    if (isNotNullish(page)) {
      page = tryIntConversion(page, `Invalid 'page' parameter value: "${page}". It must be a positive integer.`);
      if (!isValidPositiveInteger(page)) {
        throw new JsonHTTPResponseWithMessage(
          `Invalid 'page' parameter value: "${page}". It must be a positive integer.`
        );
      }
    } else {
      page = 1;
    }
  
    return queryTasks(getEts(withResults), withResults, page, per_page);
  }
  
  function isValidAllTasks(tasks: any[]): boolean {
    if (!Array.isArray(tasks)) {
      return false;
    }
  
    for (const task of tasks) {
      if (!isObject(task)) {
        return false;
      }
      
      try {
        task.id = tryIntConversion(task.id, "error" )  
      } catch (error) {
        return false
      }
      if (!isValidId(task.id)) {
        return false;
      }
      try {
        task.result_count = tryIntConversion(task.result_count, "error" )  
      } catch (error) {
        return false
      }

      if (!isValidPositiveIntegerIncludingZero(task.result_count)) {
        return false;
      }
    }
  
    return true;
  }
  
  const empty = {
    count: 0,
    total_pages: 0,
    next: null,
    previous: null,
  };
  
  function getFirstView(scraper_name: string): string | null {
    const views = Server.getViewIds(scraper_name);
    if (views) {
      return views[0];
    }
    return null;
  }

  
  
  async function cleanResultsForLargeTask(
    scraper_name: string,
    taskId: number,
    inputData: any,
    view: any,
    page: number,
    per_page: number,
    result_count: number,
    containsListField: boolean
  ): Promise<any> {
    const start = calculatePageStart(page, per_page);
    const end = calculatePageEnd(start, per_page);

    const [total_items_count, cleanedResults, hidden_fields] =await  _applyViewForUiLargeTask(
      taskId,
      view,
      Server.getViews(scraper_name),
      inputData, 
      per_page, 
      start,
      end, 
      containsListField,
    );
  
    if (containsListField) {
      result_count = total_items_count;
    }
  
    const paginatedResults = applyPagination(
      cleanedResults,
      page,
      per_page,
      hidden_fields as any,
      result_count, 
      false
    );
  
    return paginatedResults;
  }
  
  function cleanResults(
    scraper_name: string,
    results: any[],
    inputData: any,
    filters: any,
    sort: any,
    view: any,
    page: number,
    per_page: number | undefined,
    result_count: number,
    containsListField: boolean
  ): any {
    // sort than filters, maintain correct order for < 25 page limit
    results = applySorts(results, sort, Server.getSorts(scraper_name));
    results = applyFiltersInPlace(results, filters, Server.getFilters(scraper_name));
    const [cleanedResults, hidden_fields] = _applyViewForUi(
      results,
      view,
      Server.getViews(scraper_name),
      inputData
    );
  
    if (containsListField || filters) {
      result_count = cleanedResults.length;
    }
  
    const paginatedResults = applyPagination(
      cleanedResults,
      page,
      per_page,
      hidden_fields as any,
      result_count
    );
  
    return paginatedResults;
  }
  

async function performGetTaskResults(taskId: number): Promise<[string, boolean, any, number]> {
  const task = await TaskHelper.getTaskWithEntities(
    taskId,
    ['scraper_name', 'result_count', 'is_all_task', 'data'],
  );

  if (isNullish(task)) {
    throw createTaskNotFoundError(taskId);
  }

  const scraper_name = task.scraper_name;
  const task_data = task.data;
  const is_all_task = task.is_all_task;
  const result_count = task.result_count;

  return [scraper_name, is_all_task, task_data, result_count];
}

  async function executeGetTaskResults(taskId: number, jsonData: any): Promise<any> {
    const [scraper_name, _, task_data, result_count] = await performGetTaskResults(taskId);
    validateScraperName(scraper_name);
  
    const [filters, sort, view, page, per_page] = validateResultsRequest(
      jsonData,
      Server.getSortIds(scraper_name),
      Server.getViewIds(scraper_name),
      Server.getDefaultSort(scraper_name)
    ) as any;
  
    const [containsListField, results] = await retrieveTaskResults(
      taskId,
      scraper_name,
      view,
      filters,
      sort,
      page,
      per_page
    );
  
    if (!Array.isArray(results)) {
      return { ...empty, results };
    } else {
      const cleanedResults = cleanResults(
        scraper_name,
        results,
        task_data,
        filters,
        sort,
        view,
        page,
        per_page,
        result_count,
        containsListField
      );
      delete cleanedResults.hidden_fields;
      return cleanedResults;
    }
  }
  
  function generateFilename(
    taskId: number,
    view: string | null,
    is_all_task: boolean,
    task_name: string
  ): string {
    if (view) {
      view = kebabCase(view);
    }
  
    if (is_all_task) {
      return view ? `all-task-${taskId}-${view}` : `all-task-${taskId}`;
    } else {
      task_name = kebabCase(createTaskName(task_name, taskId));
      return view ? `${task_name}-${view}` : task_name;
    }
  }
  async function executeTaskResults(taskId: number, jsonData: any, reply=undefined): Promise<any> {
    let [scraper_name, status,results, inputData, is_all_task, is_large, task_name] = await performDownloadTaskResults(taskId);
    validateScraperName(scraper_name);
  
  
    // @ts-ignore
    let [fmt, filters, sort, view, convertToEnglish, downloadFolder] = validateDownloadParams(
      jsonData,
      Server.getSortIds(scraper_name),
      Server.getViewIds(scraper_name),
      Server.getDefaultSort(scraper_name)
    );
    if (!reply) {
      downloadFolder = downloadFolder ?? electronConfig.downloadsPath;
      if (!fs.existsSync(downloadFolder)) {
        return {
          path: downloadFolder,
          error: "PATH_NOT_EXISTS"
        }
      }
    }

    const views = Server.getViews(scraper_name)
    // @ts-ignore
    const filename = generateFilename(taskId, view as any, is_all_task, task_name);


    if (is_large) {
      if (!TaskResults.taskExists(taskId)) {
        throw new JsonHTTPResponseWithMessage('No Results');
      }      
      const viewObj = view && views.find(v => v.id === view);

      let streamFn;
      if (viewObj) {
        const targetFields: any[] = isNotNullish(inputData) ? getFields(viewObj.fields, inputData, []) : viewObj.fields;
        streamFn = (item: any) => {
          item = transformRecord(targetFields, item);
          return convertToEnglish ? convertUnicodeDictToAsciiDict(item) : item;
        };
      } else {
        streamFn = (item: any) => {
          return convertToEnglish ? convertUnicodeDictToAsciiDict(item) : item;
        };
      }
      if (reply){
        return downloadResultsHttp(reply,null as any, fmt, filename, taskId, is_large, streamFn);
      }
      return downloadResults(null as any, fmt, filename, taskId, is_large, streamFn, downloadFolder);
    } else {
      if (!Array.isArray(results)) {
        throw new JsonHTTPResponseWithMessage('No Results');
      }      

      if (isFailedAndNonAllTask(status, is_all_task)) {
        const error = results[0]
        throw new JsonHTTPResponseWithMessage(`Task with ID ${taskId} failed due to the following error: \n${error.message}\n. Please check the task details.`);
      }
      // filters than sort, efficent
      let cleanedResults = applyFiltersInPlace(results, filters, Server.getFilters(scraper_name));

      cleanedResults = applySorts(cleanedResults, sort, Server.getSorts(scraper_name));    
      
      [cleanedResults] = _applyViewForUi(
        cleanedResults,
        view as any,
        views,
        inputData
      );
    
      if (convertToEnglish) {
        cleanedResults = convertUnicodeDictToAsciiDictInPlace(cleanedResults);
      }
      if (reply){
        return downloadResultsHttp(reply,cleanedResults, fmt, filename, null as any, is_large, null);
      }
      return downloadResults(cleanedResults, fmt, filename, null as any, is_large, null, downloadFolder);
    }
}
  // Save MEMORY
function convertUnicodeDictToAsciiDictInPlace(inputList: any[]): any[] {
  for (let i = 0; i < inputList.length; i++) {
    inputList[i] = convertUnicodeDictToAsciiDict(inputList[i]);
  }

  return inputList;
}
  async function deleteTask(
    taskId: number,
    is_all_task: boolean,
    parentId: number | null,
    removeDuplicatesBy: any
  ): Promise<void> {
    let fn: (() => Promise<void>) | null = null;
  
    if (is_all_task) {
      await TaskHelper.deleteChildTasks(taskId);
    } else {
      if (parentId) {
        const allChildrenCount = await TaskHelper.getAllChildrenCount(parentId, taskId);
  
        if (allChildrenCount === 0) {
          await TaskHelper.deleteTask(parentId, true);
        } else {
          const hasExecutingTasks = await TaskHelper.getPendingOrExecutingChildCount(parentId, taskId);
  
          if (!hasExecutingTasks) {
            const abortedChildrenCount = await TaskHelper.getAbortedChildrenCount(parentId, taskId);
  
            if (abortedChildrenCount === allChildrenCount) {
              await TaskHelper.abortTask(parentId);
            } else {
              const failedChildrenCount = await TaskHelper.getFailedChildrenCount(parentId, taskId);
              if (failedChildrenCount) {
                fn = async () => {
                  await TaskHelper.collectAndSaveAllTask(
                    parentId,
                    taskId,
                    removeDuplicatesBy,
                    TaskStatus.FAILED
                  );
                };
              } else {
                fn = async () => {
                  await TaskHelper.collectAndSaveAllTask(
                    parentId,
                    taskId,
                    removeDuplicatesBy,
                    TaskStatus.COMPLETED
                  );
                };
              }
            }
          }
        }
      }
    }
  
    if (fn) {
      await fn();
    }
  
    await TaskHelper.deleteTask(taskId, is_all_task);
  }
  
  async function abortTask(
    taskId: number,
    is_all_task: boolean,
    parentId: number | null,
    removeDuplicatesBy: any
  ): Promise<void> {
    let fn: (() => Promise<void>) | null = null;
  
    if (is_all_task) {
      await TaskHelper.abortChildTasks(taskId);
    } else {
      if (parentId) {
        const allChildrenCount = await TaskHelper.getAllChildrenCount(parentId, taskId);
  
        if (allChildrenCount === 0) {
          await TaskHelper.abortTask(parentId);
        } else {
          const hasExecutingTasks = await TaskHelper.getPendingOrExecutingChildCount(parentId, taskId);
  
          if (!hasExecutingTasks) {
            const abortedChildrenCount = await TaskHelper.getAbortedChildrenCount(parentId, taskId);
  
            if (abortedChildrenCount === allChildrenCount) {
              await TaskHelper.abortTask(parentId);
            } else {
              const failedChildrenCount = await TaskHelper.getFailedChildrenCount(parentId, taskId);
              if (failedChildrenCount) {
                fn = async () => {
                  await TaskHelper.collectAndSaveAllTask(
                    parentId,
                    taskId,
                    removeDuplicatesBy,
                    TaskStatus.FAILED,
                  );
                };
              } else {
                fn = async () => {
                  await TaskHelper.collectAndSaveAllTask(
                    parentId,
                    taskId,
                    removeDuplicatesBy,
                    TaskStatus.COMPLETED,
                  );
                };
              }
            }
          }
        }
      }
    }
  
    if (fn) {
      await fn();
    }
  
    await TaskHelper.abortTask(taskId);
  }
  
  function executeGetAppProps(){
    const scrapers = Server.getScrapersConfig();
    const config = Server.getConfig();
    return { ...config, scrapers };
  }
  
  async function executeIsAnyTaskFinished(jsonData: any): Promise<any> {
    if (!isListOfValidIds(jsonData.pending_task_ids)) {
      throw new JsonHTTPResponseWithMessage("'pending_task_ids' must be a list of integers");
    }
    if (!isListOfValidIds(jsonData.progress_task_ids)) {
      throw new JsonHTTPResponseWithMessage("'progress_task_ids' must be a list of integers");
    }
    if (!isValidAllTasks(jsonData.all_tasks)) {
      throw new JsonHTTPResponseWithMessage(
        "'all_tasks' must be a list of dictionaries with 'id' and 'result_count' keys"
      );
    }
  
    const pendingTaskIds = jsonData.pending_task_ids;
    const progressTaskIds = jsonData.progress_task_ids;
    const allTasks = jsonData.all_tasks;
  
    const isAnyTaskFinished = await performIsAnyTaskFinished(
      pendingTaskIds,
      progressTaskIds,
      allTasks
    );
  
    return { result: isAnyTaskFinished };
  }
  
  async function executeIsTaskUpdated(jsonData: any): Promise<any> {
    const taskId = tryIntConversion(jsonData.task_id,"'task_id' must be a valid integer");;
    
    const lastUpdatedStr = jsonData.last_updated;
    const queryStatus = jsonData.status;
  
    if (!isValidId(taskId)) {
      throw new JsonHTTPResponseWithMessage("'task_id' must be a valid integer");
    }
  
    if (!isStringOfMinLength(queryStatus)) {
      throw new JsonHTTPResponseWithMessage("'status' must be a string with at least one character");
    }
  
    const lastUpdated = new Date(lastUpdatedStr);
  
    const response = await performIsTaskUpdated(taskId) as any;
    if (isNullish(response)) {
      throw createTaskNotFoundError(taskId);
    }

    const [taskUpdatedAt, taskStatus] = response
    
    const isUpdated = taskUpdatedAt > lastUpdated || taskStatus !== queryStatus;

    return { result: isUpdated };
  }
  
  const outputUiTasksEts = [
    'id',
    'status',
    'task_name',
    'result_count',
    'is_all_task',
    'finished_at',
    'started_at',
  ];
  
async function executeGetUiTasks(page: number): Promise<any> {
  if (isNotNullish(page) ) {
    page = tryIntConversion(page, "Invalid 'page' parameter. It must be a positive integer.");
    if (!isValidPositiveInteger(page)) {
      throw new JsonHTTPResponseWithMessage(
        "Invalid 'page' parameter. It must be a positive integer."
      );
        
    }
  }else{
    page = 1
  }

  return queryTasks(outputUiTasksEts, false, page, 100, serializeUiOutputTask);
}

async function executePatchTask(page: number, jsonData: any): Promise<any> {
  page = tryIntConversion(page, "Invalid 'page' parameter. Must be a positive integer.");
  if (!isValidPositiveInteger(page)) {
    throw new JsonHTTPResponseWithMessage(
      "Invalid 'page' parameter. Must be a positive integer.",
      400
    );
  }

  const [action, taskIds] = validateUiPatchTask(jsonData);

  for (const taskId of taskIds) {
    await performPatchTask(action, taskId);
  }

  return queryTasks(outputUiTasksEts, false, page, 100, serializeUiOutputTask);
}

  
  async function executeGetUiTaskResults(
    taskId: number,
    jsonData: any,
    queryParams: Record<string, any>
  ): Promise<any> {
    const [scraper_name, is_all_task, status,is_large, serializedTask, task_data, result_count] = await performGetUiTaskResults(taskId);
    validateScraperName(scraper_name);
    let [filters, sort, view, page, per_page] = validateResultsRequest(
      jsonData,
      Server.getSortIds(scraper_name),
      Server.getViewIds(scraper_name),
      Server.getDefaultSort(scraper_name)
    ) as any;
    const forceApplyFirstView = queryParams.force_apply_first_view && queryParams.force_apply_first_view.toLowerCase() === 'true';
    if (forceApplyFirstView) {
      view = getFirstView(scraper_name);
    }
    if (is_large) {
      if (!TaskResults.taskExists(taskId)) {
        return { ...empty, results: null, task: serializedTask };
      }
      
      const containsListField: any = checkViewForListField(view, scraper_name);
      const cleanedResults = await cleanResultsForLargeTask(
        scraper_name,
        taskId,
        task_data,
        view,
        page,
        per_page,
        result_count,
        containsListField
      );
      cleanedResults.task = serializedTask;
      return cleanedResults;
    }
  
    const [containsListField, results] = await retrieveTaskResults(
      taskId,
      scraper_name,
      view,
      filters,
      sort,
      page,
      per_page
    );
  
    if (!Array.isArray(results)) {
      return { ...empty, results, task: serializedTask };
    } else {
      if (isFailedAndNonAllTask(status, is_all_task)) {
        return { ...empty, results: results[0], task: serializedTask };
      }
      const cleanedResults = cleanResults(
        scraper_name,
        results,
        task_data,
        filters,
        sort,
        view,
        page,
        per_page,
        result_count,
        containsListField
      );
      cleanedResults.task = serializedTask;
      return cleanedResults;
    }
  }
  

function checkViewForListField(view: string | null, scraper_name: string): any {
  return view && findView(Server.getViews(scraper_name), view)!.containsListField
}

  async function retrieveTaskResults(
    taskId: number,
    scraper_name: string,
    view: string | null,
    filters: any,
    sort: any,
    page: number,
    per_page: number | undefined
  ): Promise<[boolean, any]> {
    // @ts-ignore
    const containsListField:any = checkViewForListField(view, scraper_name);
  
    let results: any;
    if (sort || filters || containsListField) {
      results = await TaskResults.getTask(taskId);
    } else {
      const limit = per_page ? page * per_page : null;
      results = await TaskResults.getTask(taskId, limit);
    }
    
  
    return [containsListField, results];
  }
  
  export {
    executeAsyncTask,
    executeAsyncTasks,
    executeSyncTask,
    executeSyncTasks,
    executeGetTasks,
    executeGetTaskResults,
    executeTaskResults,
    executeGetAppProps,
    executeIsAnyTaskFinished,
    executeIsTaskUpdated,
    executeGetUiTasks,
    executePatchTask,
    executeGetUiTaskResults,
    getTaskFromDb,
    performPatchTask
  };
