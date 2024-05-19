from .env import is_master, is_worker

if is_master:
    from .master_executor import MasterExecutor
    executor = MasterExecutor()
elif is_worker:
    from .worker_executor import WorkerExecutor
    executor = WorkerExecutor()
else:
    from .task_executor import TaskExecutor
    executor = TaskExecutor()
