import json
import os
from hashlib import md5
from shutil import rmtree
from json.decoder import JSONDecodeError
from .decorators_utils import create_cache_directory_if_not_exists, create_directory_if_not_exists
from .utils import read_json, relative_path
from .dontcache import DontCache

def write_json(data, path):
    with open(path, 'w', encoding="utf-8") as fp:
        json.dump(data, fp)

def getfnname(func):
    return func if isinstance(func, str) else func.__name__

def _get_cache_path(func, data):
    fn_name = getfnname(func)
    fn_cache_dir = f'cache/{fn_name}/'

    # Serialize the data to a JSON string and encode to bytes
    serialized_data = json.dumps(data).encode('utf-8')
    
    # Generate a hash from the serialized data
    data_hash = md5(serialized_data).hexdigest()

    # Create a unique cache file path with a .json extension
    cache_path = os.path.join(fn_cache_dir, data_hash + ".json")
    return cache_path

def _hash( data):
    # Serialize the data to a JSON string and encode to bytes
    serialized_data = json.dumps(data).encode('utf-8')
    
    # Generate a hash from the serialized data
    return  md5(serialized_data).hexdigest()


def _has(cache_path):
    return os.path.exists(cache_path)

def _get(cache_path):
    try:
        return read_json(cache_path)
    except JSONDecodeError:
        return None


def _read_json_files(file_paths):
    from joblib import Parallel, delayed
    results = Parallel(n_jobs=-1)(delayed(_get)(file_path) for file_path in file_paths)
    return results


def _remove(cache_path):
    if os.path.exists(cache_path):
        os.remove(cache_path)

def _delete_items(file_paths):
    from joblib import Parallel, delayed
    Parallel(n_jobs=-1)(delayed(_remove)(file_path) for file_path in file_paths)

def get_files_without_json_extension(directory_path):
    # Get a list of all files in the directory
    if not os.path.exists(directory_path):
        return []
    
    files = os.listdir(directory_path)
    
    # Use rstrip to remove the .json extension from all filenames in the list
    files_without_json_extension = [file.rstrip('.json') for file in files]
    
    return files_without_json_extension

created_fns = set()
cache_check_done = False
def _create_cache_directory_if_not_exists(func=None):
        global cache_check_done
        if not cache_check_done:
            cache_check_done = True
            create_cache_directory_if_not_exists()

        if func is not None: 
            fn_name = getfnname(func)
            
            if fn_name not in created_fns:
                created_fns.add(fn_name)
                fn_cache_dir = f'cache/{fn_name}/'
                create_directory_if_not_exists(fn_cache_dir)

def get_cached_files(func):
        fn_name = getfnname(func)
        fn_cache_dir = f'cache/{fn_name}/'
        cache_dir = relative_path(fn_cache_dir)
        results =  get_files_without_json_extension(cache_dir)
        return results

class Cache:

    REFRESH = "REFRESH"
    
    @staticmethod
    def put(func, key_data, data):
        """Write data to a cache file in JSON format."""
        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        write_json(data, path)

    @staticmethod
    def hash(data):
        return _hash(data)
              
    @staticmethod
    def has(func, key_data):
        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        return _has(path)

    @staticmethod
    def get(func, key_data):
        """Read data from a cache file."""
        
        # resolve user errors
        if isinstance(key_data, list):
            return Cache.get_items(func, key_data)

        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        if _has(path):
            return _get(path)
        return None


    @staticmethod
    def get_items(func, items=None):
        # resolve user errors
        if isinstance(items, str):
            return Cache.get_items(func, items)
                
        hashes = Cache.get_items_hashes(func, items)
        fn_name = getfnname(func)
        paths = [relative_path(f'cache/{fn_name}/{r}.json') for r in hashes]
        return _read_json_files(paths)

    @staticmethod
    def get_items_hashes(func, items=None):
        results = get_cached_files(func)

        if items is None:
            # Return all cached items
            return results
        else: 
            items  = set([Cache.hash(item) for item in items])
            return [r for r in results if r in items]

    @staticmethod
    def delete(func, key_data):
        """Remove a specific cache file."""
        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        _remove(path)

    @staticmethod
    def delete_items(func, items):

        """Remove a specific cache file."""
        hashes = Cache.get_items_hashes(func, items)
        fn_name =getfnname(func)
        paths = [relative_path(f'cache/{fn_name}/{r}.json') for r in hashes]
        _delete_items(paths)
        return len(hashes)
           
    @staticmethod
    def clear(func=None):
        """Clear all cache files. 
        If func is specified, clear cache for that specific function, 
        otherwise clear the entire cache directory."""
        global cache_check_done, created_fns

        if func is not None:
            fn_name = getfnname(func)
            fn_cache_dir = f'cache/{fn_name}/'
            cache_dir = relative_path(fn_cache_dir)
            if os.path.exists(cache_dir):
                rmtree(cache_dir, ignore_errors=True)
            if fn_name in created_fns:
                created_fns.remove(fn_name)
        else:
            cache_dir = relative_path('cache/')
            if os.path.exists(cache_dir):
                rmtree(cache_dir, ignore_errors=True)
            cache_check_done = False
            created_fns = set()
             

    @staticmethod
    def delete_items_by_filter(func, items, should_delete_item):
        # Filter items to be tested from cache
        testitems = Cache.filter_items_in_cache(func, items)
        
        # Retrieve data for the test items from cache
        testitems_data = Cache.get_items(func, testitems)
        
        # List to collect detected honeypots
        collected_honeypots = []
        
        # Iterate over each test item and its corresponding data
        for i in range(len(testitems_data)):
            # Check if the item is a honeypot based on the provided function
            if should_delete_item(testitems[i], testitems_data[i]):
                # If it's a honeypot, add it to the collected honeypots list
                collected_honeypots.append(testitems[i])

        if collected_honeypots:
            print(f"Deleting {len(collected_honeypots)} honeypots...")
            # Remove detected honeypots from cache
            Cache.delete_items(func, collected_honeypots)
            
        # Return the number of collected honeypots
        return len(collected_honeypots)
         

    @staticmethod
    def filter_items_in_cache(func, items):
        cached_items  = set(Cache.get_items_hashes(func))
        return [item for item in items if Cache.hash(item) in cached_items]

      
    @staticmethod
    def filter_items_not_in_cache(func, items):
        cached_items  = set(Cache.get_items_hashes(func))
        return [item for item in items if Cache.hash(item) not in cached_items]
                            

    @staticmethod
    def print_cached_items_count(func):
        cached_items_count  = len(get_cached_files(func))
        nm = getfnname(func)
        print(f"Number of cached items for {nm}: {cached_items_count}")
                                        