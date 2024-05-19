from bottle import run, BaseRequest
from .env import is_in_kubernetes, is_worker, is_master

BaseRequest.MEMFILE_MAX = 100 * 1024 * 1024 # 100 MB Max Data Payload

if is_master:
    from . import master_routes
elif is_worker:
    from . import worker_routes
else:
    from . import task_routes

from .executor import executor

def run_backend():
    executor.load()
    executor.start()

    host = '0.0.0.0' if is_in_kubernetes else '127.0.0.1'
    debug = False
    run(
        host=host,
        port=8000,
        debug=debug
    )