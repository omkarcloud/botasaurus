from bottle import run
from .utils.config import is_in_kubernetes, is_worker, is_master

if is_master:
    from .routes import master_routes
elif is_worker:
    from .routes import worker_routes
else:
    from .routes import task_routes

from .routes.executor import executor

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