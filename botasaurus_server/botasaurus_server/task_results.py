from json.decoder import JSONDecodeError
from .errors import JsonHTTPResponseWithMessage
from hashlib import sha256
import json
import ndjson
import os
from botasaurus.cache import read_json, _has,_remove, _delete_items, write_json
from .utils import path_task_results_tasks,path_task_results_cache

# :163941919

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
        write_json(result, task_path)
    
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
        write_json(data, task_path)
    
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
    
    @staticmethod
    def get_all_task(id, limit=None):
        # task_path = os.path.join("./", str(id) + ".ndjson")
        task_path = os.path.join(path_task_results_tasks, str(id) + ".ndjson")
        if not _has(task_path):
            return None
        items = []

        with open(task_path, 'r', encoding="utf-8") as file:
            line_number = 0
            while True:
                try:
                    line = next(file)
                    line_number += 1
                except StopIteration:
                    break
                
                line = line.strip()
                if line != "":
                    try:
                        item = json.loads(line)
                        items.append(item)
                    except json.JSONDecodeError:
                        # Handle potential malformed JSON
                        split_lines = line.split("}{")
                        
                        for i, split_line in enumerate(split_lines):
                            try:
                                if i % 2 == 0:  # Even index (including 0)
                                    split_line = split_line + "}"
                                else:  # Odd index
                                    split_line = "{" + split_line
                                
                                parsed_item = json.loads(split_line)
                                items.append(parsed_item)
                            except json.JSONDecodeError:
                                print(f"Failed to parse line {line_number}, part: {split_line}")
                    
                    if limit and len(items) >= limit:
                        break

        if limit and len(items) > limit:
            return items[:limit]
        
        return items
    @staticmethod
    def append_all_task(id, data):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".ndjson")
        if not data:
            if not _has(task_path):
                with open(task_path, 'a', encoding="utf-8") as file:
                    file.write("")
            return
        
        result = "\n".join(json.dumps(i) for i in data) + "\n"
        with open(task_path, 'a', encoding="utf-8") as file:
            file.write(result)
    @staticmethod
    def save_all_task(id, data):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".ndjson")
        with open(task_path, 'w', encoding="utf-8") as file:
            ndjson.dump(data, file)
            # fix the file
            file.write("\n")

    @staticmethod
    def delete_all_task(id):
        task_path = os.path.join(path_task_results_tasks, str(id) + ".ndjson")
        _remove(task_path)