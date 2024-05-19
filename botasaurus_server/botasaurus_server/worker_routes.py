from .executor import executor
from bottle import (
    request,
    post,
)
OK_MESSAGE = {"message": "OK"}

@post("/k8s/run-worker-task")
def k8s_run():

    task = request.json["task"]
    node_name = request.json["node_name"]

    executor.run_worker_task(task, node_name)

    return OK_MESSAGE
