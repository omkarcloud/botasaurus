from os import path, getcwd
from .env import is_master


if is_master:
    path_task_results = path.abspath(path.join(getcwd(), "..", "db", "task_results"))
else:
    path_task_results =  path.abspath(path.join(getcwd(), "task_results"))
if is_master:
    path_task_results_tasks =  path.abspath(path.join(getcwd(), "..", "db", "task_results","tasks"))
else:
    path_task_results_tasks =  path.abspath(path.join(getcwd(), "task_results","tasks"))
if is_master:
    path_task_results_cache = path.abspath(path.join(getcwd(), "..", "db", "task_results","cache"))
else:
    path_task_results_cache =  path.abspath(path.join(getcwd(), "task_results","cache"))
