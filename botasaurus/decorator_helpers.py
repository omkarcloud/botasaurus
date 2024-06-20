from typing import Callable, Optional
from functools import wraps
import traceback
from time import sleep, time
from .utils import is_errors_instance

from .cache import Cache, _get, _has, _get_cache_path, _create_cache_directory_if_not_exists
from .dontcache import is_dont_cache

def cache(_func=None, *, cache=True):
    def decorator_cache(func):
        @wraps(func)    
        def wrapper_cache(*args, **kwargs):
            nonlocal cache

            cache = kwargs.pop("cache", cache)

            if cache:
                _create_cache_directory_if_not_exists(func)

            def run_cache(*args, **kwargs):
                if cache is True:
                    path = _get_cache_path(func, [args, kwargs])
                    if _has(path):
                        return _get(path)

                result = func(*args, **kwargs)

                if cache is True or cache == 'REFRESH':
                    if is_dont_cache(result):
                        Cache.delete(func, [args, kwargs])
                    else:
                        Cache.put(func, [args, kwargs], result)

                if is_dont_cache(result):
                    result = result.data

                return result

            return run_cache(*args, **kwargs)

        return wrapper_cache

    if _func is None:
        return decorator_cache
    else:
        return decorator_cache(_func)
    
ANY = 'any'
def retry_if_is_error(instances=ANY, retries=3, wait_time=None, raise_exception=True, on_failed_after_retry_exhausted=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0

            while tries < retries:
                tries += 1
                try:
                    created_result = func(*args, **kwargs)
                    return created_result
                except Exception as e:
                    if instances != ANY:
                        errors_only_instances = list(map(lambda el: el[0] if isinstance(el, tuple) else el, instances)) if instances else []
                    if instances != ANY:
                        is_valid_error, index = is_errors_instance(errors_only_instances, e)

                        if not is_valid_error:
                            raise e
                        
                    if raise_exception:
                        traceback.print_exc()

                    if instances != ANY:
                        if instances and isinstance(instances[index], tuple):
                            instances[index][1]()

                    if tries == retries:
                        if on_failed_after_retry_exhausted is not None:
                            on_failed_after_retry_exhausted(e)
                        if raise_exception:
                            raise e

                    print('Retrying')

                    if wait_time is not None:
                        sleep(wait_time)
        return wrapper
    return decorator


def retry_on_stale_element(_func: Optional[Callable] = None, *, retries=3, wait_time=1, raise_exception=True):
    from botasaurus_driver.exceptions import DetachedElementException

    def decorator(func):
        @retry_if_is_error(
            instances=[DetachedElementException],
            retries=retries,
            wait_time=wait_time,
            raise_exception=raise_exception
        )
        @wraps(func)  # Use functools.wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def retry_on_request_failure(_func: Optional[Callable] = None, *, retries=5, wait_time=1, raise_exception=True):
    def decorator(func):
        @retry_if_is_error(
            instances=ANY,
            retries=retries,
            wait_time=wait_time,
            raise_exception=raise_exception
        )
        @wraps(func)  # Use functools.wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def measure_time(_func: Optional[Callable] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            tm  = end_time - start_time
            print(f"Execution time of {func.__name__}: {tm:.2f} seconds")
            return result

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def ignore(_func: Optional[Callable] = None, on_exception_return_Value = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:  # Catching a generic exception, can be replaced with specific exceptions
                print(f"Exception in {func.__name__}: {e}")  # Printing the exception
                result = on_exception_return_Value() if callable(on_exception_return_Value) else on_exception_return_Value
                return result

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)

