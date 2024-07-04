from datetime import datetime, timezone
from casefy import snakecase
from time import sleep
from bottle import (
    request,
    response,
    post,
    get,
    route,
    redirect,
)
import json
from sqlalchemy import  and_, or_
from .executor import executor
from .apply_pagination import apply_pagination
from .filters import apply_filters
from .sorts import apply_sorts
from .views import _apply_view_for_ui

from .download import download_results
from .server import Server
from .convert_to_english import convert_unicode_dict_to_ascii_dict

from .models import (
    Task,
    TaskStatus,
    serialize_task,
    TaskHelper,
    serialize_ui_display_task,
    serialize_ui_output_task,
)
from .db_setup import Session
from .task_results import TaskResults, create_cache_key
from .errors import JsonHTTPResponse, JsonHTTPResponseWithMessage
from .retry_on_db_error import retry_on_db_error


OK_MESSAGE = {"message": "OK"}


def serialize(data):
    if data is None:
        return None
    if isinstance(data, list):
        return [item.to_json() for item in data]
    return data.to_json()

def create_task_not_found_error(task_id):
    return JsonHTTPResponse({"status": 404, "message": f"Task {task_id} not found"}, status=404)

def jsonify(ls):
    response.content_type = "application/json"
    return json.dumps(ls)


def is_string_of_min_length(data, min_length=1):
    """Checks if data is a string with a minimum length."""
    return isinstance(data, str) and len(data) >= min_length


def ensure_json_body_is_dict(json_data):
    if json_data is None:
        raise JsonHTTPResponse({"message": "json body must be provided"}, 400)

    if not isinstance(json_data, dict):
        raise JsonHTTPResponse(
            {"message": "json body must be provided as an object"}, 400
        )


def dict_to_string(errors_dict):
    # Iterate through each key-value pair in the dictionary
    formatted_pairs = []
    for key, values in errors_dict.items():
        # Join the list of strings into a single string with semicolon and space
        value_str = "; ".join(values)
        # Format the key and the joined string
        formatted_pair = f"{key}: {value_str}"
        formatted_pairs.append(formatted_pair)

    # Join the formatted pairs with a comma and a newline
    result_string = ", \n".join(formatted_pairs)

    return result_string


def validate_scraper_name(scraper_name):
    valid_scraper_names = Server.get_scrapers_names()
    
    if len(valid_scraper_names) == 0:
            error_message = "No Scrapers are available."
            raise JsonHTTPResponse({"message": error_message}, 400)
    
    valid_names_string = ", ".join(valid_scraper_names)
    if scraper_name is None:
        if len(valid_scraper_names) == 1:
            scraper_name = valid_scraper_names[0]
        else:
            error_message = f"'scraper_name' must be provided when there are multiple scrapers. The scraper_name must be one of {valid_names_string}."
            raise JsonHTTPResponse({"message": error_message}, 400)
    elif not Server.get_scraper(scraper_name):
        
        if len(valid_scraper_names) == 1:
            error_message = f"A scraper with the name '{scraper_name}' does not exist. The scraper_name must be {valid_names_string}."
        else:
            error_message = f"A scraper with the name '{scraper_name}' does not exist. The scraper_name must be one of {valid_names_string}."

        raise JsonHTTPResponse({"message": error_message}, 400)
    return scraper_name

def validate_task_request(json_data):
    """Validates the task request data."""

    ensure_json_body_is_dict(json_data)

    scraper_name = json_data.get("scraper_name")
    data = json_data.get("data")

    scraper_name = validate_scraper_name(scraper_name)

    if data is None:
        raise JsonHTTPResponse({"message": "'data' key must be provided"}, 400)

    if not isinstance(data, dict):
        raise JsonHTTPResponse(
            {"message": "'data' key must be a valid JSON object"}, 400
        )

    controls = Server.get_controls(scraper_name)

    result = controls.getBackendValidationResult(data, timeout=300).valueOf()

    errors = result["errors"]

    if errors != {}:
        raise JsonHTTPResponse({"message": dict_to_string(errors)}, 400)

    data = result["data"]
    metadata = result["metadata"]
    return scraper_name, data, metadata

def create_tasks(scraper, data, metadata, is_sync):
    create_all_tasks = scraper["create_all_task"]
    split_task = scraper["split_task"]
    scraper_name = scraper["scraper_name"]
    scraper_type = scraper["scraper_type"]
    get_task_name = scraper["get_task_name"]

    
    all_task_sort_id  =  int(datetime.now(timezone.utc).timestamp())
    all_task = None
    all_task_id = None
    if create_all_tasks:
        all_task, all_task_id = perform_create_all_task(data, metadata, is_sync, scraper_name, scraper_type, all_task_sort_id)

    if split_task:
        tasks_data = split_task(data)
        if len(tasks_data) == 0:
            return [], [], split_task
    else:
        tasks_data = [data]
            
    def createTask(task_data, sort_id):
                task_name = get_task_name(task_data) if get_task_name else None
                return Task(
                status=TaskStatus.PENDING,
                scraper_name=scraper_name,
                task_name=task_name,
                scraper_type=scraper_type,
                is_all_task=False,
                is_sync=is_sync,
                parent_task_id=all_task_id,
                data=task_data,
                meta_data=metadata,
                sort_id=sort_id,  # Set the sort_id for the child task

            )

    def create_cached_tasks(task_datas):
                ls = []
                cache_keys = []
                
                for t in task_datas:
                    key = create_cache_key(scraper_name, t)
                    ls.append({'key': key, 'task_data': t})
                    cache_keys.append(key)
                
                cache_items_len, cache_map = create_cache_details(cache_keys)
                
                tasks = []

                def create_cached_task(task_data, cached_result, sort_id):
                    now_time = datetime.now(timezone.utc)
                    task_name = get_task_name(task_data) if get_task_name else None
                    return Task(
                            status=TaskStatus.COMPLETED,
                            scraper_name=scraper_name,
                            task_name=task_name,
                            scraper_type=scraper_type,
                            is_all_task=False,
                            is_sync=is_sync,
                            parent_task_id=all_task_id,
                            data=task_data,
                            meta_data=metadata,
                            result_count=len(cached_result),
                            started_at=now_time,
                            finished_at=now_time,
                            sort_id=sort_id,  # Set the sort_id for the cached task

                        )
                cached_tasks = []
                for idx, item in enumerate(ls):
                    cached_result = cache_map.get(item['key'])
                    if cached_result:
                        sort_id = all_task_sort_id - (idx + 1)
                        ts = create_cached_task(item['task_data'], cached_result, sort_id)
                        ts.result = cached_result
                        tasks.append(ts)
                        cached_tasks.append(ts)
                    else:
                        sort_id = all_task_sort_id - (idx + 1)
                        tasks.append(createTask(item['task_data'], sort_id))
                
                return tasks, cached_tasks,cache_items_len

    if Server.cache:
            tasks, cached_tasks, cached_tasks_len = create_cached_tasks(tasks_data)
            tasks = perform_create_tasks(tasks, cached_tasks)
    else: 
            tasks = []
            for idx, task_data in enumerate(tasks_data):
                # Assign sort_id for the non-cached task
                sort_id = all_task_sort_id - (idx + 1)
                tasks.append(createTask(task_data, sort_id))
            cached_tasks_len = 0
       
            tasks = perform_create_tasks(tasks)

    # here write results with help of cachemap
    if cached_tasks_len > 0:
        tasklen = len(tasks)
        if tasklen == cached_tasks_len:
            print('All Tasks Results are Returned from cache')
        else:
            print(f'{cached_tasks_len} out of {tasklen} Results are Returned from cache')
        if all_task_id:
            perform_complete_task(all_task_id, Server.get_remove_duplicates_by(scraper_name))

    tasks_with_all_task = tasks
    if all_task_id:
        tasks_with_all_task = [all_task] + tasks

    return tasks_with_all_task, tasks, split_task

@retry_on_db_error
def perform_complete_task(all_task_id
                          ,remove_duplicates_by=None

                          ):
    with Session() as session:
        executor.complete_parent_task_if_possible(session, all_task_id,remove_duplicates_by)
        session.commit()



def save(x):
    """Copy a file from source to destination."""
    TaskResults.save_task(x[0],x[1],)

def parallel_create_files(file_list):
    """

    Copy files in parallel.

    Parameters:
    file_list (list of dict): List of dictionaries with 'source_file' and 'destination_file' keys.
    """
    from joblib import Parallel, delayed
    Parallel(n_jobs=-1)(delayed(save)(file) for file in file_list)


@retry_on_db_error
def perform_create_tasks(tasks, cached_tasks = None):
    with Session() as session:
        session.add_all(tasks)
        session.commit()
        
        if cached_tasks:
            file_list = [ (t.id, t.result,) for t in cached_tasks]
            parallel_create_files(file_list)

        # basically here we will write cache, as each cached task adds a property called __cached__result = None [default]
        # but it set when going over cache
        return serialize(tasks)

def create_cache_details(cache_keys):
    existing_items = TaskResults.filter_items_in_cache(cache_keys)

    cache_items = TaskResults.get_cached_items_json_filed(existing_items)
    cache_items_len = len(cache_items)
    cache_map = {cache['key']: cache['result'] for cache in cache_items}
    return cache_items_len, cache_map

@retry_on_db_error
def perform_create_all_task(data, metadata, is_sync, scraper_name, scraper_type, all_task_sort_id):
    with Session() as session:
            all_task = Task(
                    status=TaskStatus.PENDING,
                    scraper_name=scraper_name,
                    scraper_type=scraper_type,
                    is_all_task=True,
                    is_sync=is_sync,
                    parent_task_id=None,
                    data=data,
                    meta_data=metadata,
                    task_name="All Task",
                    sort_id=all_task_sort_id,  # Set the sort_id for the all task
                )
            session.add(all_task)
            session.commit()

            all_task_id = all_task.id
            return serialize(all_task),all_task_id


@get("/")
def home():
    return redirect("/api")


@get("/api")
def get_api():
    return OK_MESSAGE


def create_async_task(validated_data):
    scraper_name, data, metadata = validated_data

    tasks_with_all_task, tasks, split_task = create_tasks(
        Server.get_scraper(scraper_name), data, metadata, False
    )

    if split_task:
        return tasks_with_all_task
    else:
        return tasks[0]


@post("/api/tasks/create-task-async")
def submit_async_task():

    json_data = request.json

    if isinstance(json_data, list):
        validated_data_items = [validate_task_request(item) for item in json_data]
        result = [
            create_async_task(validated_data_item)
            for validated_data_item in validated_data_items
        ]
        return jsonify(result)
    else:
        result = create_async_task(validate_task_request(request.json))
        return jsonify(result)

@retry_on_db_error
def refetch_tasks(item):
    with Session() as session:
        if isinstance(item, list):
            ids = [i["id"] for i in item]
            tasks = TaskHelper.get_tasks_by_ids(session, ids)
            return serialize(tasks)
        else:
            task = TaskHelper.get_task(session, item["id"])
            return serialize(task)


@post("/api/tasks/create-task-sync")
def submit_sync_task():
    json_data = request.json

    if isinstance(json_data, list):
        validated_data_items = [validate_task_request(item) for item in json_data]
        
        ts = []
        for validated_data_item in validated_data_items:
            scraper_name, data, metadata = validated_data_item
            ts.append(
                create_tasks(Server.get_scraper(scraper_name), data, metadata, True)
            )

        # wait for completion
        for t in ts:
            tasks_with_all_task, tasks, split_task = t

            if tasks_with_all_task and tasks_with_all_task[0]['is_all_task']:
                wait_tasks = [tasks_with_all_task[0]]
            else:
                wait_tasks = tasks

            for task in wait_tasks:
                task_id = task["id"]
                while True:
                    if is_task_done(task_id):
                        break
                    sleep(0.1)
        # give results
        rst = []
        for t in ts:

            tasks_with_all_task, tasks, split_task = t

            if split_task:
                rst.append(refetch_tasks(tasks_with_all_task))
            else:
                rst.append(refetch_tasks(tasks[0]))

        return jsonify(rst)
    else:
        scraper_name, data, metadata = validate_task_request(request.json)

        tasks_with_all_task, tasks, split_task = create_tasks(
            Server.get_scraper(scraper_name), data, metadata, True
        )

        if tasks_with_all_task and tasks_with_all_task[0]['is_all_task']:
            wait_tasks = [tasks_with_all_task[0]]
        else:
            wait_tasks = tasks

        for task in wait_tasks:
            task_id = task["id"]
            while True:
                if is_task_done(task_id):
                    break
                sleep(0.1)

        if split_task:
            return jsonify(refetch_tasks(tasks_with_all_task))
        else:
            return jsonify(refetch_tasks(tasks[0]))
@retry_on_db_error
def is_task_done(task_id):
    with Session() as session:
        x  =  TaskHelper.is_task_completed_or_failed(session, task_id)
    return x

def get_ets(with_results):  
        if with_results:
            return [
                Task.id,
                Task.status,
                Task.task_name,
                Task.scraper_name,
                Task.result_count,
                Task.scraper_type,
                Task.is_all_task,
                Task.is_sync,
                Task.parent_task_id,
                Task.data,
                Task.meta_data,
                Task.finished_at,
                Task.started_at,
                Task.created_at,
                Task.updated_at,
            ]
        else:
            return [
                Task.id,
                Task.status,
                Task.task_name,
                Task.scraper_name,
                Task.result_count,
                Task.scraper_type,
                Task.is_all_task,
                Task.is_sync,
                Task.parent_task_id,
                Task.data,
                Task.meta_data,
                Task.finished_at,
                Task.started_at,
                Task.created_at,
                Task.updated_at,
            ]

def create_page_url(page, per_page, with_results):
                query_params = {}

                if page:
                    query_params["page"] = page

                if per_page is not None:
                    query_params["per_page"] = per_page

                if not with_results:
                    query_params["with_results"] = False

                if query_params != {}:
                    return query_params


@retry_on_db_error
def queryTasks(ets, with_results,  page=None, per_page=None, serializer = serialize_task):
    with Session() as session:
        
        tasks_query = session.query(Task).with_entities(*ets)
        total_count = tasks_query.count()

        if per_page is None:
            per_page = 1 if total_count == 0 else total_count 
            page = 1
        else: 
            per_page = int(per_page)
        
        total_pages = max((total_count + per_page - 1) // per_page, 1)

        
        page = int(page)
        page = max(min(page, total_pages), 1)  # Ensure page is within valid range

        # Apply pagination if page and per_page are provided and valid
        tasks_query = tasks_query.order_by(Task.sort_id.desc())
        if per_page is not None:
            per_page = int(per_page)
            start = (page - 1) * per_page
            tasks_query = tasks_query.limit(per_page).offset(start)
        
        tasks = tasks_query.all()
        
        current_page = page if page is not None else 1
        next_page = current_page + 1 if (current_page * per_page) < total_count else None
        previous_page = current_page - 1 if current_page > 1 else None
        
        if next_page:
            next_page = create_page_url(next_page, per_page, with_results)
        
        if previous_page:
            previous_page = create_page_url(previous_page, per_page, with_results)

        return jsonify(
                    {
                        "count": total_count,
                        "total_pages":total_pages,
                        "next": next_page,
                        "previous": previous_page,
                        "results": [
                            serializer(task, with_results) for task in tasks
                        ]
                    }
                )

def is_valid_positive_integer(param):
    try:
        return int(param) > 0
    except (ValueError, TypeError):
        return False
    

def is_valid_positive_integer_including_zero(param):
    try:
        return int(param) >= 0
    except (ValueError, TypeError):
        return False
        
    
@get("/api/tasks")
def get_tasks():
    with_results = request.query.get("with_results", "true").lower() == "true"
    page = request.query.get("page")
    per_page = request.query.get("per_page")

    if per_page is not None:
        if not is_valid_positive_integer(per_page):
            raise JsonHTTPResponseWithMessage("Invalid 'per_page' parameter. It must be a positive integer.")
    else:
        page = 1
        per_page = None
    # Validate page and per_page
    if page is not None:
    # Check if any pagination parameter is provided
        if not is_valid_positive_integer(page):
            raise JsonHTTPResponseWithMessage("Invalid 'page' parameter. It must be a positive integer.")
    else:
        page = 1
    
    return queryTasks(get_ets(with_results),  with_results, page, per_page)

@retry_on_db_error
def get_task_from_db(task_id):
    with Session() as session:
        task = TaskHelper.get_task(session, task_id)
        if task:
            return serialize(task)
        else:
            raise create_task_not_found_error(task_id)

@get("/api/tasks/<task_id:int>")
def get_task(task_id):
    return get_task_from_db(task_id)

def is_valid_all_tasks(tasks):
    if not isinstance(tasks, list):
        return False

    for task in tasks:
        if not isinstance(task, dict):
            return False

        if not is_valid_positive_integer(task.get("id")):
            return False
        else:
            task["id"] = int(task["id"])

        if not is_valid_positive_integer_including_zero(task.get("result_count")):
            return False
        else: 
            task["result_count"] = int(task["result_count"])
    return True

@retry_on_db_error
def perform_is_task_updated(task_id):
    with Session() as session:
        task_data = session.query(Task.updated_at, Task.status).filter(Task.id == task_id).first()
    return task_data


def validate_filters(json_data):
    filters = json_data.get("filters")
    if filters:  # Only validate if it exists
        if not isinstance(filters, dict):
            raise JsonHTTPResponse({"message": "Filters must be a dictionary"}, 400)
    return filters

def validate_view(json_data, allowed_views):
    view = json_data.get("view")

    if view:
        if not is_string_of_min_length(view):
            raise JsonHTTPResponse(
                {"message": "View must be a string with at least one character"}, 400
            )

        view = view.lower()
        if view not in allowed_views:
            raise JsonHTTPResponse(
                {
                    "message": f"Invalid view. Must be one of: {', '.join(allowed_views)}."
                },
                400,
            )
            
    return view

def validate_sort(json_data, allowed_sorts, default_sort):
    sort = json_data.get("sort", default_sort)
    
    if sort == 'no_sort':
        sort = None
    elif sort:
        if not is_string_of_min_length(sort):
            raise JsonHTTPResponse(
                {"message": "Sort must be a string with at least one character"}, 400
            )

        sort = sort.lower()
        if sort not in allowed_sorts:
            raise JsonHTTPResponse(
                {
                    "message": f"Invalid sort. Must be one of: {', '.join(allowed_sorts)}."
                },
                400,
            )
    else:
        sort = default_sort
    return sort

def validate_results_request(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates parameters for a task results request (excluding format)."""

    ensure_json_body_is_dict(json_data)  # Assuming you have this helper

    # Filters Validation (if applicable)
    filters = validate_filters(json_data)

    # Sort Validation (if applicable)
    sort = validate_sort(json_data, allowed_sorts, default_sort)
    # View Validation (if applicable)
    view = validate_view(json_data, allowed_views)

    # Offset Validation
    page = json_data.get("page") 
    if page is not None:
        try:
            page = int(page)
        except ValueError:
            raise JsonHTTPResponse({"message": "page must be an integer"}, 400)
        if not is_valid_positive_integer(page):
            raise JsonHTTPResponseWithMessage("page must be greater than or equal to 1")
    else:
        page = 1

    per_page = json_data.get("per_page") 
    if per_page is not None:
        try:
            per_page = int(per_page)
        except ValueError:
            raise JsonHTTPResponse({"message": "per_page must be an integer"}, 400)
        if per_page <= 0:
            raise JsonHTTPResponse(
                {"message": "per_page must be greater than or equal to 1"}, 400
            )

    return filters, sort, view, page, per_page



empty = {"count": 0, "total_pages": 0, "next": None, "previous": None,}


def get_first_view(scraper_name):
    views = Server.get_view_ids(scraper_name)
    if views:
        return views[0]
    return None

def clean_results(scraper_name, results, forceApplyFirstView,input_data):
    filters, sort, view, page, per_page = validate_results_request(
        request.json,
        Server.get_sort_ids(scraper_name),
        Server.get_view_ids(scraper_name),
        Server.get_default_sort(scraper_name),
    )
    
    if forceApplyFirstView:
        view = get_first_view(scraper_name)

    # Apply sorts, filters, and view
    results = apply_sorts(results, sort, Server.get_sorts(scraper_name))
    results = apply_filters(results, filters, Server.get_filters(scraper_name))
    results, hidden_fields = _apply_view_for_ui(results, view, Server.get_views(scraper_name),input_data )
    
    
    results = apply_pagination(results, page, per_page, hidden_fields)
    return results


@retry_on_db_error
def perform_get_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(session, task_id, [Task.scraper_name ,Task.data ])
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        results = TaskResults.get_task(task_id)
    return scraper_name,results,task_data
@post("/api/tasks/<task_id:int>/results")
def get_task_results(task_id):
    scraper_name, results, task_data = perform_get_task_results(task_id)
    validate_scraper_name(scraper_name)
    if not isinstance(results, list):
        return jsonify({**empty, "results":results})

    results = clean_results(scraper_name, results, False, task_data)
    del results['hidden_fields']
    return jsonify(results)


def validate_download_params(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates download parameters for a task."""

    ensure_json_body_is_dict(json_data)

    # Format Validation
    fmt = json_data.get("format")
    
    if not fmt:
        fmt = "json"
    elif not is_string_of_min_length(fmt):  # Assuming you have this helper function
        raise JsonHTTPResponse(
            {"message": "Format must be a string with at least one character"}, 400
        )
    elif fmt == "xlsx":
        fmt = "excel"

    fmt = fmt.lower()
    if fmt not in ["json", "csv", "excel"]:
        raise JsonHTTPResponse(
            {"message": "Invalid format.  Must be one of: JSON, CSV, Excel"}, 400
        )

    # Filters Validation (if applicable)
    filters = validate_filters(json_data)

    # Sort Validation (if applicable)
    sort = validate_sort(json_data, allowed_sorts, default_sort)
    # View Validation (if applicable)
    view = validate_view(json_data, allowed_views)

    # Convert to English Validation (if applicable)
    convert_to_english = json_data.get("convert_to_english", True)
    if not isinstance(convert_to_english, bool):
        raise JsonHTTPResponse({"message": "convert_to_english must be a boolean"}, 400)

    return fmt, filters, sort, view, convert_to_english


def generate_filename(task_id, view, scraper_name):
    scraper_name = snakecase(Server.get_scraper(scraper_name)["name"])

    filename = f"task_{task_id}"

    if view:
        # Assuming view has already been validated and converted to lowercase
        filename = f"{view}_task_{task_id}"

    return filename


@post("/api/tasks/<task_id:int>/download")
def download_task_results(task_id):

    scraper_name, results,task_data = perform_download_task_results(task_id)
    validate_scraper_name(scraper_name)
    if not isinstance(results, list):
        raise JsonHTTPResponse('No Results')

    fmt, filters, sort, view, convert_to_english = validate_download_params(
        request.json,
        Server.get_sort_ids(scraper_name),
        Server.get_view_ids(scraper_name),
        Server.get_default_sort(scraper_name),
    )

    # Apply sorts, filters, and view
    results = apply_sorts(results, sort, Server.get_sorts(scraper_name))
    results = apply_filters(results, filters, Server.get_filters(scraper_name))
    results,_ = _apply_view_for_ui(results, view, Server.get_views(scraper_name), task_data)

    if convert_to_english:
        results = convert_unicode_dict_to_ascii_dict(results)

    filename = generate_filename(task_id, view, scraper_name)

    return download_results(results, fmt, filename)

@retry_on_db_error
def perform_download_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(session, task_id, [Task.scraper_name ,Task.data ])
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        results = TaskResults.get_task(task_id)
    return scraper_name,results,task_data

def delete_task(session, task_id, is_all_task, parent_id,remove_duplicates_by):
    if is_all_task:
        TaskHelper.delete_child_tasks(session, task_id)
    else:

        if parent_id:
            all_children_count = TaskHelper.get_all_children_count(
                session, parent_id, task_id
            )

            if all_children_count == 0:
                TaskHelper.delete_task(session, parent_id)
            else:
                has_executing_tasks = TaskHelper.get_pending_or_executing_child_count(
                    session, parent_id, task_id
                )

                if not has_executing_tasks:
                    aborted_children_count = TaskHelper.get_aborted_children_count(
                        session, parent_id, task_id
                    )

                    if aborted_children_count == all_children_count:
                        TaskHelper.abort_task(session, parent_id)
                    else:
                        failed_children_count = TaskHelper.get_failed_children_count(
                            session, parent_id, task_id
                        )
                        if failed_children_count:
                            TaskHelper.fail_task(session, parent_id)
                        else:
                            TaskHelper.success_all_task(session, parent_id, task_id, remove_duplicates_by)

    TaskHelper.delete_task(session, task_id)


def abort_task(session, task_id, is_all_task, parent_id, remove_duplicates_by):

    if is_all_task:
        TaskHelper.abort_child_tasks(session, task_id)
    else:
        if parent_id:
            all_children_count = TaskHelper.get_all_children_count(
                session, parent_id, task_id
            )

            if all_children_count == 0:
                TaskHelper.abort_task(session, parent_id)
            else:
                has_executing_tasks = TaskHelper.get_pending_or_executing_child_count(
                    session, parent_id, task_id
                )

                if not has_executing_tasks:
                    aborted_children_count = TaskHelper.get_aborted_children_count(
                        session, parent_id, task_id
                    )

                    if aborted_children_count == all_children_count:
                        TaskHelper.abort_task(session, parent_id)
                    else:
                        failed_children_count = TaskHelper.get_failed_children_count(
                            session, parent_id, task_id
                        )
                        if failed_children_count:
                            TaskHelper.fail_task(session, parent_id)
                        else:
                            TaskHelper.success_all_task(session, parent_id, task_id, remove_duplicates_by)

    TaskHelper.abort_task(session, task_id)


def is_list_of_integers(obj):
    return isinstance(obj, list) and all(isinstance(item, int) for item in obj)


def validate_patch_task(json_data):
    ensure_json_body_is_dict(json_data)

    task_ids = json_data.get("task_ids")

    if not task_ids:
        raise JsonHTTPResponse({"message": "'task_ids' must be provided"}, 400)

    if not is_list_of_integers(task_ids):
        raise JsonHTTPResponse(
            {"message": "'task_ids' must be a list of integers"}, 400
        )

    return task_ids

@retry_on_db_error
def perform_patch_task(action, task_id):
    with Session() as session:
        task = session.query(Task.id, Task.is_all_task, Task.parent_task_id, Task.scraper_name, ).filter(Task.id == task_id).first()
        if task:

            remove_duplicates_by = Server.get_remove_duplicates_by(task[-1])
            task = task[0:3]
            if action == "delete":
                delete_task(session, *task, remove_duplicates_by)
            elif action == "abort":
                abort_task(session, *task, remove_duplicates_by)
            session.commit()

@route("/api/tasks/<task_id:int>/abort", method="PATCH")
def abort_single_task(task_id):
    perform_patch_task("abort", task_id)
    return OK_MESSAGE

@route("/api/tasks/<task_id:int>", method="DELETE")
def delete_single_task(task_id):
    perform_patch_task("delete", task_id)
    return OK_MESSAGE

@route("/api/tasks/bulk-abort", method="POST")
def bulk_abort_tasks():
    task_ids = validate_patch_task(request.json)

    for task_id in task_ids:
        perform_patch_task("abort", task_id)

    return OK_MESSAGE

@route("/api/tasks/bulk-delete", method="POST")
def bulk_delete_tasks():
    task_ids = validate_patch_task(request.json)

    for task_id in task_ids:
        perform_patch_task("delete", task_id)

    return OK_MESSAGE


@get("/api/ui/config")
def get_api_config():
    scrapers = Server.get_scrapers_config()
    config = Server.get_config()
    return {**config, "scrapers": scrapers}



@post("/api/ui/tasks/is-any-task-updated")  # Add this route
def is_any_task_finished():
    json_data = request.json

    if not is_list_of_integers(json_data.get("pending_task_ids")):
        raise JsonHTTPResponse(
            {"message": "'pending_task_ids' must be a list of integers"}, 400
        )
    if not is_list_of_integers(json_data.get("progress_task_ids")):
        raise JsonHTTPResponse(
            {"message": "'progress_task_ids' must be a list of integers"}, 400
        )

    if not is_valid_all_tasks(json_data.get("all_tasks")):
        raise JsonHTTPResponse(
            {"message": "'all_tasks' must be a list of dictionaries with 'id' and 'result_count' keys"}, 400
        )

    pending_task_ids = json_data["pending_task_ids"]
    progress_task_ids = json_data["progress_task_ids"]
    all_tasks = json_data["all_tasks"]
    
    is_any_task_finished = perform_is_any_task_finished(pending_task_ids, progress_task_ids, all_tasks)

    return jsonify({"result": is_any_task_finished})

@retry_on_db_error
def perform_is_any_task_finished(pending_task_ids, progress_task_ids, all_tasks):
    with Session() as session:
        all_tasks_query = [and_(Task.id == x['id'], Task.result_count >  x['result_count']) for x in all_tasks]
        is_any_task_finished = session.query(Task.id).filter(
            or_(
                and_(Task.id.in_(pending_task_ids), Task.status != TaskStatus.PENDING),
                and_(Task.id.in_(progress_task_ids), Task.status != TaskStatus.IN_PROGRESS),
                *all_tasks_query
            )
        ).first() is not None
        
    return is_any_task_finished

@post("/api/ui/tasks/is-task-updated")
def is_task_updated():
    # Extract 'task_id' and 'last_updated' from query parameters
    task_id = request.json.get("task_id")
    last_updated_str = request.json.get("last_updated")
    query_status = request.json.get("status")  # Extract the 'status' parameter

    # Validate 'task_id' using is_valid_integer
    if not is_valid_positive_integer(task_id):
        raise JsonHTTPResponse({"message": "'task_id' must be a valid integer"}, 400)


    # Validate 'task_id' using is_valid_integer
    if not is_string_of_min_length(query_status):
        raise JsonHTTPResponse(
            {"message": "'status' must be a string with at least one character"}, 400
        )

    # Convert 'task_id' to integer
    task_id = int(task_id)

    
    # Parse 'last_updated' using fromisoformat
    try:
        last_updated = datetime.fromisoformat(last_updated_str)  # Strip 'Z' if present
        last_updated = last_updated.replace(tzinfo=None)  # Make 'last_updated' naive for comparison
    except ValueError:
        raise JsonHTTPResponse({"message": "'last_updated' must be in valid ISO 8601 format"}, 400)

    # Query the database for the task's 'updated_at' timestamp using the given 'task_id'
    task_data = perform_is_task_updated(task_id)

    if not task_data:
        raise create_task_not_found_error(task_id)
    
    task_updated_at, task_status = task_data
    task_updated_at = task_updated_at.replace(tzinfo=None)  # Make 'task_updated_at' naive for comparison
    
    if (task_updated_at > last_updated) or (task_status != query_status):
      is_updated = True
    else:
      is_updated = False
          
    return jsonify({"result": is_updated})




def validate_ui_patch_task(json_data):
    ensure_json_body_is_dict(json_data)

    action = json_data.get("action")
    task_ids = json_data.get("task_ids")

    if not action:
        raise JsonHTTPResponse({"message": "'action' must be provided"}, 400)

    if not isinstance(action, str):
        raise JsonHTTPResponse({"message": "'action' must be a string"}, 400)
    action = action.lower()
    if action not in ["abort", "delete"]:
        raise JsonHTTPResponse(
            {"message": '\'action\' must be either "abort" or "delete"'}, 400
        )

    if not task_ids:
        raise JsonHTTPResponse({"message": "'task_ids' must be provided"}, 400)

    if not is_list_of_integers(task_ids):
        raise JsonHTTPResponse(
            {"message": "'task_ids' must be a list of integers"}, 400
        )

    return action, task_ids
output_ui_tasks_ets = [
                Task.id,
                Task.status,
                Task.task_name,
                Task.result_count,
                Task.is_all_task,
                Task.finished_at,
                Task.started_at,
            ]

@get("/api/ui/tasks")
def get_ui_tasks():
    page = request.query.get("page")

    # Validate page and per_page
    if page is not None:
    # Check if any pagination parameter is provided
        if not is_valid_positive_integer(page):
            raise JsonHTTPResponseWithMessage("Invalid 'page' parameter. It must be a positive integer.")
    else:
        page = 1
    
    return queryTasks(output_ui_tasks_ets, False, page, 100, serialize_ui_output_task)

@route("/api/ui/tasks", method="PATCH")
def patch_task():
    # This is done to return the tasks after the patch operation for purpose of faster ui response.
    page = request.query.get("page")
    if not (is_valid_positive_integer(page)):
          raise JsonHTTPResponseWithMessage("Invalid 'page' parameter. Must be a positive integer.")

    action, task_ids = validate_ui_patch_task(request.json)

    for task_id in task_ids:
        perform_patch_task(action, task_id)

    return queryTasks( output_ui_tasks_ets, False, page, 100, serialize_ui_output_task)

@retry_on_db_error
def perform_get_ui_task_results(task_id):
    with Session() as session:
        task = TaskHelper.get_task_with_entities(session, task_id, [Task.scraper_name ,Task.data,Task.updated_at, Task.status ])
        if not task:
            raise create_task_not_found_error(task_id)

        scraper_name = task.scraper_name
        task_data = task.data
        results =  TaskResults.get_task(task_id)
        serialized_task = serialize_ui_display_task(task)
    return scraper_name,results,serialized_task,task_data

@post("/api/ui/tasks/<task_id:int>/results")
def get_ui_task_results(task_id):
    scraper_name, results, serialized_task, task_data = perform_get_ui_task_results(task_id)
    validate_scraper_name(scraper_name)
    foreceApplyFirstView = request.query.get("force_apply_first_view","none").lower() == "true"
    
    
    if not isinstance(results, list):
        return jsonify({**empty, "results": results, "task":serialized_task })

    results = clean_results(scraper_name, results, foreceApplyFirstView, task_data)
    results["task"] = serialized_task
    return jsonify(results)