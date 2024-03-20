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
from .executor import executor
from .apply_offset_limit import apply_offset_limit
from .filters import apply_filters
from .sorts import apply_sorts
from .views import apply_view

from .download import download_results
from .server import Server
from .convert_to_english import convert_unicode_dict_to_ascii_dict

from .models import (
    Cache,
    Task,
    create_cache_key,
    TaskStatus,
    serialize_task,
    TaskHelper,
)
from .db_setup import Session
from .errors import JsonHTTPResponse, JsonHTTPResponseWithMessage


TASK_NOT_FOUND = {"status": 404, "message": "Task not found"}
OK_MESSAGE = {"message": "OK"}


def serialize(data):
    if data is None:
        return None
    if isinstance(data, list):
        return [item.to_json() for item in data]
    return data.to_json()


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
    if not scraper_name:
        raise JsonHTTPResponse({"message": "'scraper_name' must be provided"}, 400)

    if not is_string_of_min_length(scraper_name):
        raise JsonHTTPResponse(
            {"message": "'scraper_name' must be a string with at least one character"},
            400,
        )

    if not Server.get_scraper(scraper_name):
        valid_scraper_names = Server.get_scrapers_names()
        valid_names_string = ", ".join(valid_scraper_names)

        if len(valid_scraper_names) == 0:
            error_message = "No Scrapers are available."
        elif len(valid_scraper_names) == 1:
            error_message = f"A scraper with the name '{scraper_name}' does not exist. The scraper_name must be {valid_names_string}."
        else:
            error_message = f"A scraper with the name '{scraper_name}' does not exist. The scraper_name must be one of {valid_names_string}."

        raise JsonHTTPResponse({"message": error_message}, 400)


def validate_task_request(json_data):
    """Validates the task request data."""

    ensure_json_body_is_dict(json_data)

    scraper_name = json_data.get("scraper_name")
    data = json_data.get("data")

    validate_scraper_name(scraper_name)

    if data is None:
        raise JsonHTTPResponse({"message": "'data' key must be provided"}, 400)

    if not isinstance(data, dict):
        raise JsonHTTPResponse(
            {"message": "'data' key must be a valid JSON object"}, 400
        )

    controls = Server.get_controls(scraper_name)

    result = controls.getBackendValidationResult(data).valueOf()

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

    if split_task:
        tasks_data = split_task(data)
        if len(tasks_data) == 0:
            return [], [], split_task
    else:
        tasks_data = [data]
    
    all_task_sort_id  =  int(datetime.now(timezone.utc).timestamp())
    with Session() as db:
        all_task = None
        all_task_id = None
        if create_all_tasks:
            all_task = Task(
                status=TaskStatus.PENDING,
                scraper_name=scraper_name,
                scraper_type=scraper_type,
                is_all_task=True,
                is_sync=is_sync,
                parent_task_id=None,
                data=data,
                meta_data=metadata,
                result=None,
                task_name="All Task",
                sort_id=all_task_sort_id,  # Set the sort_id for the all task
            )
            db.add(all_task)
            db.commit()

            all_task_id = all_task.id

            
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
                result=None,
                sort_id=sort_id,  # Set the sort_id for the child task

            )

        def create_cached_tasks(session, task_datas):
                ls = []
                cache_keys = []
                
                for t in task_datas:
                    key = create_cache_key(scraper_name, t)
                    ls.append({'key': key, 'task_data': t})
                    cache_keys.append(key)
                
                cache_items = session.query(Cache).filter(Cache.key.in_(cache_keys)).all()
                cache_items_len = len(cache_items)
                cache_map = {cache.key: cache.result for cache in cache_items}
                
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
                            result=cached_result,
                            result_count=len(cached_result),
                            started_at=now_time,
                            finished_at=now_time,
                            sort_id=sort_id,  # Set the sort_id for the cached task

                        )
                
                for idx, item in enumerate(ls):
                    cached_result = cache_map.get(item['key'])
                    if cached_result:
                        sort_id = all_task_sort_id - (idx + 1)
                        tasks.append(create_cached_task(item['task_data'], cached_result, sort_id))
                    else:
                        sort_id = all_task_sort_id - (idx + 1)
                        tasks.append(createTask(item['task_data'], sort_id))
                
                return tasks, cache_items_len

        if Server.cache:
            tasks, cached_tasks_len = create_cached_tasks(db, tasks_data)
        else: 
            tasks = []
            for idx, task_data in enumerate(tasks_data):
                # Assign sort_id for the non-cached task
                sort_id = all_task_sort_id - (idx + 1)
                tasks.append(createTask(task_data, sort_id))
            cached_tasks_len = 0
       

        db.add_all(tasks)
        db.commit()

        if cached_tasks_len > 0:
            tasklen = len(tasks)
            if tasklen == cached_tasks_len:
                print('All Tasks Results are Returned from cache')
            else:
                print(f'{cached_tasks_len} out of {tasklen} Results are Returned from cache')

            executor.complete_parent_task_if_possible(db, all_task_id)

        db.commit()
        tasks = serialize(tasks)
        all_task = serialize(all_task)

    tasks_with_all_task = tasks
    if all_task:
        tasks_with_all_task = [all_task] + tasks

    return tasks_with_all_task, tasks, split_task


@get("/")
def home():
    return redirect("/api")


@get("/api")
def get_api():
    return OK_MESSAGE


@get("/api/config")
def get_api_config():
    scrapers = Server.get_scrapers_config()
    config = Server.get_config()
    return {**config, "scrapers": scrapers}

def create_async_task(validated_data):
    scraper_name, data, metadata = validated_data

    tasks_with_all_task, tasks, split_task = create_tasks(
        Server.get_scraper(scraper_name), data, metadata, False
    )

    if split_task:
        return tasks_with_all_task
    else:
        return tasks[0]


@post("/api/tasks/submit-async")
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


def refetch_tasks(item):
    with Session() as session:
        if isinstance(item, list):
            ids = [i["id"] for i in item]
            tasks = TaskHelper.get_tasks_by_ids(session, ids)
            return serialize(tasks)
        else:
            task = TaskHelper.get_task(session, item["id"])
            return serialize(task)


@post("/api/tasks/submit-sync")
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
                    with Session() as session:
                        if TaskHelper.is_task_completed_or_failed(session, task_id):
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
                with Session() as session:
                    if TaskHelper.is_task_completed_or_failed(session, task_id):
                        break
                sleep(0.1)

        if split_task:
            return jsonify(refetch_tasks(tasks_with_all_task))
        else:
            return jsonify(refetch_tasks(tasks[0]))




def queryTasks(with_results, sort_by_date, page=None, per_page=None):
    with Session() as session:
        if with_results:
            ets = [
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
                Task.result,
                Task.finished_at,
                Task.started_at,
                Task.created_at,
                Task.updated_at,
            ]
        else:
            ets = [
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

        tasks_query = session.query(Task).with_entities(*ets)
        total_count = tasks_query.count()

        if sort_by_date:
            tasks_query = tasks_query.order_by(Task.sort_id.desc())

        # Apply pagination if page and per_page are provided and valid
        if page is not None and per_page is not None:
            per_page = int(per_page)
            page = int(page)
            tasks_query = tasks_query.limit(per_page).offset((page - 1) * per_page)
            total_pages = max((total_count + per_page - 1) // per_page, 1)
        else:
            total_pages = 1

        tasks = tasks_query.all()
        

        return jsonify(
                    {
                        "results": [
                            serialize_task(task, with_result=with_results) for task in tasks
                        ],
                        "total_pages":total_pages
                    }
                )

def is_valid_integer(param):
    try:
        return int(param) > 0
    except (ValueError, TypeError):
        return False
    
    
@get("/api/tasks")
def get_tasks():
    with_results = request.query.get("with_results", "true").lower() == "true"
    sort_by_date = request.query.get("sort_by_date", "true").lower() == "true"
    page = request.query.get("page")
    per_page = request.query.get("per_page")

    # Validate page and per_page
    if page or per_page:  # Check if any pagination parameter is provided
        if not (is_valid_integer(page) and is_valid_integer(per_page)):
            raise JsonHTTPResponseWithMessage("Invalid 'page' or 'per_page' parameter. Both must be positive integers.")

    return queryTasks(with_results, sort_by_date, page, per_page)

@get("/api/tasks/<task_id:int>")
def get_task(task_id):
    with Session() as session:
        task = TaskHelper.get_task(session, task_id)
        if task:
            return serialize(task)
        else:
            raise JsonHTTPResponse(TASK_NOT_FOUND, status=TASK_NOT_FOUND["status"])


def validate_download_params(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates download parameters for a task."""

    ensure_json_body_is_dict(json_data)

    # Format Validation
    fmt = json_data.get("format")
    if not fmt:
        raise JsonHTTPResponse({"message": "Format is required"}, 400)

    if not is_string_of_min_length(fmt):  # Assuming you have this helper function
        raise JsonHTTPResponse(
            {"message": "Format must be a string with at least one character"}, 400
        )

    fmt = fmt.lower()
    if fmt not in ["json", "csv", "excel"]:
        raise JsonHTTPResponse(
            {"message": "Invalid format.  Must be one of: JSON, CSV, Excel"}, 400
        )

    # Filters Validation (if applicable)
    filters = json_data.get("filters")
    if filters:  # Only validate if it exists
        if not isinstance(filters, dict):
            raise JsonHTTPResponse({"message": "Filters must be a dictionary"}, 400)


    if "sort" not in json_data:
        sort = default_sort
    else:
        sort = json_data.get("sort")
    if sort:
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

    # View Validation (if applicable)
    view = json_data.get("view")

    if view == "__all_fields__":
        view = None
    elif view:
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
    else: 
        if allowed_views:
            view = allowed_views[0]
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

    with Session() as session:
        task = TaskHelper.get_task(session, task_id)
        if not task:
            raise JsonHTTPResponse(TASK_NOT_FOUND, status=TASK_NOT_FOUND["status"])

        scraper_name = task.scraper_name
        results = task.result
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
    results = apply_view(results, view, Server.get_views(scraper_name))

    if convert_to_english:
        results = convert_unicode_dict_to_ascii_dict(results)

    filename = generate_filename(task_id, view, scraper_name)

    return download_results(results, fmt, filename)


def validate_results_request(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates parameters for a task results request (excluding format)."""

    ensure_json_body_is_dict(json_data)  # Assuming you have this helper

    # Filters Validation (if applicable)
    filters = json_data.get("filters")
    if filters:  # Only validate if it exists
        if not isinstance(filters, dict):
            raise JsonHTTPResponse({"message": "Filters must be a dictionary"}, 400)

    # Sort Validation (if applicable)

    if "sort" not in json_data:
        sort = default_sort
    else:
        sort = json_data.get("sort")
    
    if sort:
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

    # View Validation (if applicable)
    view = json_data.get("view")

    if view == "__all_fields__":
        view = None
    elif view:
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
    else: 
        if allowed_views:
            view = allowed_views[0]


    # Offset Validation
    offset = json_data.get("offset", 0)  # Default to 0 if missing
    try:
        offset = int(offset)
    except ValueError:
        raise JsonHTTPResponse({"message": "Offset must be an integer"}, 400)
    if offset < 0:
        raise JsonHTTPResponse(
            {"message": "Offset must be greater than or equal to 0"}, 400
        )

    # Limit Validation
    DEFAULT_LIMIT = 25
    limit = json_data.get("limit", DEFAULT_LIMIT)  # Default to 1000 if missing
    try:
        limit = int(limit)
    except ValueError:
        raise JsonHTTPResponse({"message": "Limit must be an integer"}, 400)
    if limit < 1:
        raise JsonHTTPResponse(
            {"message": "Limit must be greater than or equal to 1"}, 400
        )

    return filters, sort, view, offset, limit


empty = {"count": 0, "page_count": 0, "next": None, "previous": None,}


@post("/api/tasks/<task_id:int>/results")
def get_task_results(task_id):

    with Session() as session:
        task = TaskHelper.get_task(session, task_id)
        if not task:
            raise JsonHTTPResponse(TASK_NOT_FOUND, status=TASK_NOT_FOUND["status"])

        scraper_name = task.scraper_name
        results = task.result
        serialized_task = serialize_task(task, False)
    validate_scraper_name(scraper_name)
    if not isinstance(results, list):
        return jsonify({**empty, "results":results, "task":serialized_task })

    filters, sort, view, offset, limit = validate_results_request(
        request.json,
        Server.get_sort_ids(scraper_name),
        Server.get_view_ids(scraper_name),
        Server.get_default_sort(scraper_name),
    )
    # Apply sorts, filters, and view
    results = apply_sorts(results, sort, Server.get_sorts(scraper_name))
    results = apply_filters(results, filters, Server.get_filters(scraper_name))
    results = apply_view(results, view, Server.get_views(scraper_name))

    results = apply_offset_limit(results, offset, limit)
    results["task"] = serialized_task
    return jsonify(results)


def delete_task(session, task):
    task_id = task.id
    if task.is_all_task:
        TaskHelper.delete_child_tasks(session, task_id)
    else:
        parent_id = task.parent_task_id
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
                            TaskHelper.success_all_task(session, parent_id, task_id)

    TaskHelper.delete_task(session, task_id)


def abort_task(session, task):
    task_id = task.id

    if task.is_all_task:
        TaskHelper.abort_child_tasks(session, task_id)
    else:
        parent_id = task.parent_task_id
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
                            TaskHelper.success_all_task(session, parent_id, task_id)

    TaskHelper.abort_task(session, task_id)


def is_list_of_integers(obj):
    return isinstance(obj, list) and all(isinstance(item, int) for item in obj)


def validate_patch_task(json_data):
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

@route("/api/tasks", method="PATCH")
def patch_task():
    action, task_ids = validate_patch_task(request.json)

    for task_id in task_ids:
        with Session() as session:
            task = session.get(Task, task_id)
            if task:
                if action == "delete":
                    delete_task(session, task)
                elif action == "abort":
                    abort_task(session, task)
            session.commit()

    return_tasks = request.query.get("return_tasks", "false").lower() == "true"    
    if return_tasks:
      page = request.query.get("page",)
      if not (is_valid_integer(page)):
            raise JsonHTTPResponseWithMessage("Invalid 'page' parameter. Must be a positive integer.")
      return queryTasks(False, True, page, 100)
    return OK_MESSAGE
