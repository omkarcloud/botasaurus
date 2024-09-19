from bottle import (
    request,
    response,
    post,
    get,
    route,
    redirect,
)
from .errors import add_cors_headers
from .validation import (
    validate_patch_task,
)
from .routes_db_logic import (
    execute_async_task,
    execute_async_tasks,
    execute_get_api_config,
    execute_get_task_results,
    execute_get_tasks,
    execute_get_ui_task_results,
    execute_get_ui_tasks,
    execute_is_any_task_finished,
    execute_is_task_updated,
    execute_patch_task,
    execute_sync_task,
    execute_sync_tasks,
    execute_task_results,
    get_task_from_db,
    perform_patch_task,
    OK_MESSAGE,
)
import json
import bottle



@route("/<:path>", method="OPTIONS")
def enable_cors_generic_route():
    """
    This route takes priority over all others. So any request with an OPTIONS
    method will be handled by this function.

    See: https://github.com/bottlepy/bottle/issues/402

    NOTE: This means we won't 404 any invalid path that is an OPTIONS request.
    """
    add_cors_headers(response.headers)

@bottle.hook("after_request")
def enable_cors_after_request_hook():
    """
    This executes after every route. We use it to attach CORS headers when
    applicable.
    """
    add_cors_headers(response.headers)

def jsonify(ls):
    response.content_type = "application/json"
    return json.dumps(ls)

@get("/")
def home():
    return redirect("/api")

@get("/api")
def get_api():
    return OK_MESSAGE

@post("/api/tasks/create-task-async")
def create_async_task():
    json_data = request.json

    if isinstance(json_data, list):
        result = execute_async_tasks(json_data)
        return jsonify(result)
    else:
        result = execute_async_task(json_data)
        return jsonify(result)

@post("/api/tasks/create-task-sync")
def create_sync_task():
    json_data = request.json

    if isinstance(json_data, list):
        rst = execute_sync_tasks(json_data)
        return jsonify(rst)
    else:
        final = execute_sync_task(json_data)
        return jsonify(final)


@get("/api/tasks")
def get_tasks():
    query_params = request.query
    return execute_get_tasks(query_params)


@get("/api/tasks/<task_id:int>")
def get_task(task_id):
    return get_task_from_db(task_id)

@post("/api/tasks/<task_id:int>/results")
def get_task_results(task_id):
    json_data = request.json
    results = execute_get_task_results(task_id, json_data)
    return jsonify(results)


@post("/api/tasks/<task_id:int>/download")
def download_task_results(task_id):
    json_data = request.json
    return execute_task_results(task_id, json_data)


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
    json_data = request.json
    task_ids = validate_patch_task(json_data)

    for task_id in task_ids:
        perform_patch_task("abort", task_id)

    return OK_MESSAGE

@route("/api/tasks/bulk-delete", method="POST")
def bulk_delete_tasks():
    json_data = request.json
    task_ids = validate_patch_task(json_data)

    for task_id in task_ids:
        perform_patch_task("delete", task_id)

    return OK_MESSAGE

@get("/api/ui/config")
def get_api_config():
    result = execute_get_api_config()
    return result


@post("/api/ui/tasks/is-any-task-updated")  # Add this route
def is_any_task_updated():
    json_data = request.json
    result = execute_is_any_task_finished(json_data)
    return jsonify(result)


@post("/api/ui/tasks/is-task-updated")
def is_task_updated():
    # Extract 'task_id' and 'last_updated' from query parameters
    json_data = request.json
    result = execute_is_task_updated(json_data)
    return jsonify(result)

@get("/api/ui/tasks")
def get_tasks_for_ui_display():
    query_params = request.query
    page = query_params.get("page")
    result = execute_get_ui_tasks(page)
    return result

@route("/api/ui/tasks", method="PATCH")
def patch_task():
    # This is done to return the tasks after the patch operation for purpose of faster ui response.
    query_params = request.query
    page = query_params.get("page")
    json_data = request.json

    result = execute_patch_task(page, json_data)
    return result


@post("/api/ui/tasks/<task_id:int>/results")
def get_ui_task_results(task_id):

    json_data = request.json
    query_params = request.query

    final = execute_get_ui_task_results(task_id, json_data, query_params)
    return jsonify(final)