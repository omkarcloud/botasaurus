from json.decoder import JSONDecodeError
import shutil
import sys
from .errors import JsonHTTPResponseWithMessage
from hashlib import sha256
import json
import os
from botasaurus.cache import   read_json, _has,_remove, _delete_items
from .utils import path_task_results_tasks,path_task_results_cache


def safe_json_write(data, target_file):

    # Convert data to JSON string
    json_data = json.dumps(data)
    
    # Check the size of the JSON data
    size_in_bytes = sys.getsizeof(json_data)
    size_in_mb = size_in_bytes / (1024 * 1024)
    if size_in_mb > 10:
        # If greater than 10 MB, write to a temporary file then move it
        temp_file = target_file.rstrip('.json')  + "-temp.json"
        with open(temp_file, 'w', encoding="utf-8") as f:
            f.write(json_data)
        # Move the temp file to the target location, overwrite if exists
        shutil.move(temp_file, target_file)
    else:
        # If not greater than 10 MB, write directly to the target file
        # This will overwrite the file if it already exists
        with open(target_file, 'w', encoding="utf-8") as f:
            f.write(json_data)


def _get(cache_path):
    try:
        return read_json(cache_path)
    except JSONDecodeError:
        # Instead of returning None when a JSONDecodeError occurs,
        # it's better to handle the error or notify the user.
        # Here, we raise a custom exception to notify that the JSON is invalid.
        raise JsonHTTPResponseWithMessage(f"Invalid JSON format in file: {cache_path}")


def _read_json_files(file_paths):
            from joblib import Parallel, delayed
            results = Parallel(n_jobs=-1)(delayed(_get)(file_path) for file_path in file_paths)
            return results

def _get_task(id):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".json")
        if not _has(task_path):
            return None
            # raise JsonHTTPResponseWithMessage(f"No task with id:{id} found.")
        return _get(task_path)


def create_cache_key(scraper_name, data):
    return (
        scraper_name
        + "-"
        + sha256(json.dumps(data, sort_keys=True).encode()).hexdigest() + ".json"
    )

def generate_cached_task_path(scraper_name, data):
        key = create_cache_key(scraper_name, data)
        task_path = os.path.join(path_task_results_cache, key )
        return task_path

def get_files():
    return os.listdir(path_task_results_cache)

def _read_json_files_dict(file_paths):
            from joblib import Parallel, delayed
            results = Parallel(n_jobs=-1)(delayed(lambda item: {"key":item, "result": _get( os.path.join(path_task_results_cache, item )) })(file_path) for file_path in file_paths)
            return results

class TaskResults:

    @staticmethod
    def filter_items_in_cache(items):
        cached_items  = set(get_files())
        return [item for item in items if item in cached_items]

    # caches
    @staticmethod
    def save_cached_task(scraper_name, data, result):
        task_path = generate_cached_task_path(scraper_name, data)
        safe_json_write(result, task_path)
    
    @staticmethod
    def get_cached_items(scraper_name, items):
        keys = [generate_cached_task_path(scraper_name, item) for item in items]
        return _read_json_files(keys)

    
    @staticmethod
    def get_cached_items_json_filed(items):
        return _read_json_files_dict(items)
        
    # tasks
    @staticmethod
    def save_task(id, data):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".json")
        safe_json_write(data, task_path)
    
    @staticmethod
    def get_task(id):
        return _get_task(id)

    @staticmethod
    def get_tasks(ids):
        paths = [os.path.join(path_task_results_tasks, str(id) + ".json") for id in ids]
        return _read_json_files(paths)

    @staticmethod
    def delete_task(id):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".json")
        _remove(task_path)
    
    @staticmethod
    def delete_tasks(ids):
        paths = [os.path.join(path_task_results_tasks, str(id) + ".json") for id in ids]
        return _delete_items(paths)
