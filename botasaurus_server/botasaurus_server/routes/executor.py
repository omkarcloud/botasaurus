from ..utils.config import is_master, is_worker

if is_master:
    from ..executors.master_executor import MasterExecutor
    executor = MasterExecutor()
elif is_worker:
    from ..executors.worker_executor import WorkerExecutor
    executor = WorkerExecutor()
else:
    from ..executors.task_executor import TaskExecutor
    executor = TaskExecutor()
