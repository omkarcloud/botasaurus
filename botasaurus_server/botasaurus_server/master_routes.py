from .validation import OK_MESSAGE # imports all routes as well
from .executor import executor
from bottle import (
    request,
    post,
)

@post("/k8s/success")
def k8s_success():
    json_data = request.json

    task_id = json_data["task_id"]
    task_type = json_data["task_type"]
    task_result = json_data["task_result"]
    scraper_name = json_data["scraper_name"]
    data = json_data["data"]
    node_name = json_data["node_name"]

    executor.on_success(task_id, task_type, task_result, node_name,scraper_name, data)

    return OK_MESSAGE


@post("/k8s/fail")
def k8s_fail():

    json_data = request.json
    task_id = json_data["task_id"]
    task_type = json_data["task_type"]
    task_result = json_data["task_result"]
    node_name = json_data["node_name"]

    executor.on_failure(task_id, task_type, task_result, node_name)

    return OK_MESSAGE