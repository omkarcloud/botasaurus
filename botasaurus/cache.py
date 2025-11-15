import json
import os
from hashlib import md5
from shutil import rmtree
from json.decoder import JSONDecodeError
from .output import get_output_directory, get_output_path
from .decorators_utils import create_directory_if_not_exists
from .utils import read_json, relative_path, write_json as format_write_json
from .dontcache import DontCache


class CacheMissException(Exception):
    """Exception raised when an item is not found in the cache."""
    def __init__(self, key):
        self.key = key
        super().__init__(f"Cache miss for key: '{key}'")

def get_directory_path(file_path):
    return os.path.dirname(file_path)

def write_json(data, path):
    try:
        with open(path, 'w', encoding="utf-8") as fp:
            json.dump(data, fp)
    except FileNotFoundError:
        create_directory_if_not_exists(get_directory_path(path))
        return write_json(data, path)


def getfnname(func):
    return func if isinstance(func, str) else func.__name__

def _get_cache_path(func, data):
    fn_name = getfnname(func)
    fn_cache_dir = f'{Cache.cache_directory}{fn_name}/'

    # Serialize the data to a JSON string and encode to bytes
    serialized_data = json.dumps(data).encode('utf-8')
    
    # Generate a hash from the serialized data
    data_hash = md5(serialized_data).hexdigest()
    if Cache.cache_directory == "cache/":
      cache_path = os.path.join(fn_cache_dir, data_hash + ".json")
    else:
      cache_path = os.path.join(relative_path(fn_cache_dir), data_hash + ".json")
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
    except (JSONDecodeError, FileNotFoundError):
        # These are files which are corrupted, likely as user paused when files were being written.
        _remove(cache_path)
        raise CacheMissException(cache_path)

def safe_get(cache_path):
    try:
        return read_json(cache_path)
    except (JSONDecodeError, FileNotFoundError):
        _remove(cache_path)
        # These are files which are corrupted, likely as user paused when files were being written.
        return None

def _read_json_files(file_paths):
    from joblib import Parallel, delayed
    results = Parallel(n_jobs=-1)(delayed(safe_get)(file_path) for file_path in file_paths)
    return results

def safe_corrupted_get(cache_path):
    try:
        read_json(cache_path)
        return 0
    except (JSONDecodeError, FileNotFoundError):
        _remove(cache_path)
        # These are files which are corrupted, likely as user paused when files were being written.
        return 1
    
def _delete_corrupted_cached_items(file_paths):
    from joblib import Parallel, delayed
    results = Parallel(n_jobs=-1)(delayed(safe_corrupted_get)(file_path) for file_path in file_paths)
    return results

def _remove(cache_path):
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
        except FileNotFoundError:
            pass
# used by decorators 
def _put(result, cache_path):
    write_json(result, cache_path)
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

def is_affirmative(input_string):
    # List of affirmative representations
    affirmative_values = {"true", "yes", "y", "1", "yeah", "yep", "sure", "ok", "okay", "affirmative", "t"}

    # Normalize the input string to lowercase and strip any extra whitespace
    normalized_string = input_string.strip().lower()

    # Check if the normalized string is in the set of affirmative values
    return normalized_string in affirmative_values

def pluralize(word, n):
        return word if n <= 1 else word + 's'
def is_negative(input_string):
    # List of negative representations
    negative_values = {"false", "no", "n", "0", "nah", "nope", "never", "negative", "f"}

    # Normalize the input string to lowercase and strip any extra whitespace
    normalized_string = input_string.strip().lower()

    # Check if the normalized string is in the set of negative values
    return normalized_string in negative_values

created_fns = set()
cache_check_done = False
def _create_cache_directory_if_not_exists(func=None):
        global cache_check_done
        if not cache_check_done:
            cache_check_done = True
            create_directory_if_not_exists(Cache.cache_directory)

        if func is not None: 
            fn_name = getfnname(func)
            
            if fn_name not in created_fns:
                created_fns.add(fn_name)
                fn_cache_dir = f'{Cache.cache_directory}{fn_name}/'
                create_directory_if_not_exists(fn_cache_dir)

def get_cached_files(func):
        fn_name = getfnname(func)
        fn_cache_dir = f'{Cache.cache_directory}{fn_name}/'
        cache_dir = relative_path(fn_cache_dir)
        results =  get_files_without_json_extension(cache_dir)
        return results

def _delete_items_by_filter(func, items, should_delete_item):
        # Filter items to be tested from cache
        testitems = Cache.filter_items_in_cache(func, items)
        
        # Retrieve data for the test items from cache
        # testitems_data = Cache.get_items(func, testitems)
        
        # List to collect detected honeypots
        collected_honeypots = []
        # print(len(testitems))
        # Iterate over each test item and its corresponding data
        for i in range(len(testitems)):
            # Check if the item is a honeypot based on the provided function
            key = testitems[i]
            try:
              data = Cache.get(func, key)
            except CacheMissException:
              continue
            
            if should_delete_item(key, data):
                # If it's a honeypot, add it to the collected honeypots list
                collected_honeypots.append(testitems[i])

        if collected_honeypots:
            if get_output_directory() == "output/":
                path = "./output/items_to_be_deleted.json"
            else: 
                path = get_output_path("items_to_be_deleted.json")
            format_write_json(collected_honeypots, path)
            while True:
                result = input(f"Should we delete {len(collected_honeypots)} items in {path}? (Y/n): ")

                if is_affirmative(result):
                    item_plural = pluralize('item', len(collected_honeypots))
                    print(f"Deleting {len(collected_honeypots)} {item_plural}...")
                    Cache.delete_items(func, collected_honeypots)
                    break
                elif is_negative(result):
                    print("No items were deleted")
                    break
                    
        else:
            print("No items were deleted")
        # Return the number of collected honeypots
        return len(collected_honeypots)   

def _delete_items_by_filter_no_items(func, should_delete_item):
        # Filter items to be tested from cache
        testitems = Cache.get_items_hashes(func)
        
        # Retrieve data for the test items from cache
        # testitems_data = Cache.get_items(func, testitems)
        
        # List to collect detected honeypots
        collected_honeypots = []
        # print(len(testitems))
        # Iterate over each test item and its corresponding data
        for i in range(len(testitems)):
            # Check if the item is a honeypot based on the provided function
            key = testitems[i]
            try:
              data = Cache.get_item_by_hash(func, key)
            except CacheMissException:
              continue
            
            if should_delete_item(key, data):
                # If it's a honeypot, add it to the collected honeypots list
                collected_honeypots.append(testitems[i])

        if collected_honeypots:
            if get_output_directory() == "output/":
                path = "./output/items_to_be_deleted.json"
            else: 
                path = get_output_path("items_to_be_deleted.json")
            format_write_json(collected_honeypots, path)
            while True:
                result = input(f"Should we delete {len(collected_honeypots)} items in {path}? (Y/n): ")

                if is_affirmative(result):
                    item_plural = pluralize('item', len(collected_honeypots))
                    print(f"Deleting {len(collected_honeypots)} {item_plural}...")
                    Cache.delete_items_by_hashes(func, collected_honeypots)
                    break
                elif is_negative(result):
                    print("No items were deleted")
                    break
                    
        else:
            print("No items were deleted")
        # Return the number of collected honeypots
        return len(collected_honeypots)     
class Cache:
    cache_directory = 'cache/'  # Default cache folder

    REFRESH = "REFRESH"
    
    @staticmethod
    def set_cache_directory(folder):
        """Set the cache folder for all cache operations."""
        Cache.cache_directory = str(folder).rstrip('/') + '/'

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
    def get(func, key_data, raise_exception=True):
        """Read data from a cache file."""
        
        # resolve user errors
        if isinstance(key_data, list):
            return Cache.get_items(func, key_data)

        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        if _has(path):
            try:
              return _get(path)
            except CacheMissException:
              return None
        
        if raise_exception:
            raise CacheMissException(path)
        return None
    @staticmethod
    def get_item_by_hash(func, hash, raise_exception=True):
        """Read data from a cache file."""
        
        _create_cache_directory_if_not_exists(func)
        path = Cache.generate_cache_path_from_hash(func, hash)
        if _has(path):
            try:
              return _get(path)
            except CacheMissException:
              return None
        
        if raise_exception:
            raise CacheMissException(path)
        return None    

    @staticmethod
    def get_items(func, items=None, max=None):
        # resolve user errors
        if isinstance(items, str):
            return Cache.get_items(func, items)

        hashes = Cache.get_items_hashes(func, items)
        if max is not None:
            hashes = hashes[:max]
        fn_name = getfnname(func)
        paths = [relative_path(f'{Cache.cache_directory}{fn_name}/{r}.json') for r in hashes]
        return _read_json_files(paths)

    @staticmethod
    def delete_corrupted_items(func):
        hashes = Cache.get_items_hashes(func, None)
        fn_name = getfnname(func)
        paths = [relative_path(f'{Cache.cache_directory}{fn_name}/{r}.json') for r in hashes]
        corrupted_items_removed = sum(_delete_corrupted_cached_items(paths))
        if corrupted_items_removed:
            item_plural = pluralize('item', corrupted_items_removed)
            print(f"Deleted {corrupted_items_removed} corrupted {item_plural}")
        else:
          print("No corrupted items found")        
    
        return corrupted_items_removed

    @staticmethod
    def generate_cache_path_from_hash(func, hash):
        func = getfnname(func)
        return relative_path(f'{Cache.cache_directory}{func}/{hash}.json')

    @staticmethod
    def get_random_items(func, n=5):
        import random

        hashes = Cache.get_items_hashes(func, None)
        if n is not None:
            hashes = random.sample(hashes, n)
        else: 
            random.shuffle(hashes)

        fn_name = getfnname(func)
        paths = [relative_path(f'{Cache.cache_directory}{fn_name}/{r}.json') for r in hashes]
        return _read_json_files(paths)
    @staticmethod
    def get_items_hashes(func, items=None):

        if items is None:
            results = get_cached_files(func)
            # Return all cached items
            return results
        else: 
            # bug fixed, which causes bad cached items order
            return [Cache.hash(item) for item in items]

    @staticmethod
    def _get_item_modified_time(func, key_data):
        """
        Private function to get the timestamp when cache was stored.
        Returns the modification time of the cache file as a datetime object.
        """
        from datetime import datetime
        
        _create_cache_directory_if_not_exists(func)
        path = _get_cache_path(func, key_data)
        
        if not _has(path):
            raise CacheMissException(path)
        
        # Get file modification time
        timestamp = os.path.getmtime(path)
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def is_item_older_than(func, key_data, days=0, seconds=0, microseconds=0, 
                            milliseconds=0, minutes=0, hours=0, weeks=0):
        """
        Check if cached item is older than the specified time period.
        
        Args:
            func: The function name or object
            key_data: The cache key
            days: Number of days (default: 0)
            seconds: Number of seconds (default: 0)
            microseconds: Number of microseconds (default: 0)
            milliseconds: Number of milliseconds (default: 0)
            minutes: Number of minutes (default: 0)
            hours: Number of hours (default: 0)
            weeks: Number of weeks (default: 0)
        
        Returns:
            bool: True if cache is older than specified time period, False otherwise
            
        Raises:
            CacheMissException: If cache doesn't exist
        """
        from datetime import datetime, timedelta
        
        # Create timedelta from parameters
        time_delta = timedelta(
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks
        )
        
        # Get cache timestamp
        cache_time = Cache._get_item_modified_time(func, key_data)
        
        # Compare with current time
        age = datetime.now() - cache_time
        
        return age > time_delta

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
        fn_name = getfnname(func)
        paths = [relative_path(f'{Cache.cache_directory}{fn_name}/{r}.json') for r in hashes]
        _delete_items(paths)
        return len(hashes)
           
    @staticmethod
    def delete_items_by_hashes(func, hashes):
        """Remove a specific cache file."""
        fn_name = getfnname(func)
        paths = [relative_path(f'{Cache.cache_directory}{fn_name}/{r}.json') for r in hashes]
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
            fn_cache_dir = f'{Cache.cache_directory}{fn_name}/'
            cache_dir = relative_path(fn_cache_dir)
            if os.path.exists(cache_dir):
                rmtree(cache_dir, ignore_errors=True)
            if fn_name in created_fns:
                created_fns.remove(fn_name)
        else:
            cache_dir = relative_path(Cache.cache_directory)
            if os.path.exists(cache_dir):
                rmtree(cache_dir, ignore_errors=True)
            cache_check_done = False
            created_fns = set()

    # @staticmethod
    # def delete_items_by_filter(func, items, should_delete_item):
    #     # Filter items to be tested from cache
    #     testitems = Cache.filter_items_in_cache(func, items)
        
    #     # Retrieve data for the test items from cache
    #     testitems_data = Cache.get_items(func, testitems)
        
    #     # List to collect detected honeypots
    #     collected_honeypots = []
        
    #     # Iterate over each test item and its corresponding data
    #     for i in range(len(testitems_data)):
    #         # Check if the item is a honeypot based on the provided function
    #         if should_delete_item(testitems[i], testitems_data[i]):
    #             # If it's a honeypot, add it to the collected honeypots list
    #             collected_honeypots.append(testitems[i])

    #     if collected_honeypots:
    #         print(f"Deleting {len(collected_honeypots)} honeypots...")
    #         # Remove detected honeypots from cache
    #         Cache.delete_items(func, collected_honeypots)
            
    #     # Return the number of collected honeypots
    #     return len(collected_honeypots)


    @staticmethod
    def delete_items_by_filter(func, should_delete_item, items=None):
        if items == None:
            return _delete_items_by_filter_no_items(func, should_delete_item)
        else:
            return _delete_items_by_filter(func, items, should_delete_item)
     
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
        return cached_items_count

    @staticmethod
    def get_cached_items_count(func):
        cached_items_count  = len(get_cached_files(func))
        return cached_items_count