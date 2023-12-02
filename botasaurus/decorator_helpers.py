from typing import Callable, Optional
from selenium.common.exceptions import  StaleElementReferenceException
from functools import wraps
import traceback
from time import sleep

def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1


def retry_if_is_error(instances=None, retries=3, wait_time=None, raise_exception=True, on_failed_after_retry_exhausted=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            errors_only_instances = list(map(lambda el: el[0] if isinstance(el, tuple) else el, instances)) if instances else []

            while tries < retries:
                tries += 1
                try:
                    created_result = func(*args, **kwargs)
                    return created_result
                except Exception as e:
                    is_valid_error, index = is_errors_instance(errors_only_instances, e)

                    if not is_valid_error:
                        raise e
                    if raise_exception:
                        traceback.print_exc()

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
    def decorator(func):
        @retry_if_is_error(
            instances=[StaleElementReferenceException],
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