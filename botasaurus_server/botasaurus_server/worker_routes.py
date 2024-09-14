from .executor import executor
from bottle import (
    request,
    post,
)
OK_MESSAGE = {"message": "OK"}

@post("/k8s/run-worker-task")
def k8s_run():
    json_data = request.json

    task = json_data["task"]
    node_name = json_data["node_name"]

    executor.run_worker_task(task, node_name)

    return OK_MESSAGE
