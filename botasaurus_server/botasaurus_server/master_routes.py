from .task_routes import OK_MESSAGE # imports all routes as well
from .executor import executor
from bottle import (
    request,
    post,
)

@post("/k8s/success")
def k8s_success():

    task_id = request.json["task_id"]
    task_type = request.json["task_type"]
    task_result = request.json["task_result"]
    node_name = request.json["node_name"]

    executor.on_success(task_id, task_type, task_result, node_name)

    return OK_MESSAGE


@post("/k8s/fail")
def k8s_fail():

    task_id = request.json["task_id"]
    task_type = request.json["task_type"]
    task_result = request.json["task_result"]
    node_name = request.json["node_name"]

    executor.on_failure(task_id, task_type, task_result, node_name)

    return OK_MESSAGE