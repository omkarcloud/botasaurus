from functools import wraps
import os
import signal
from time import sleep
import traceback
from typing import Callable, Optional
from sqlalchemy.exc import OperationalError

def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1

ANY = 'any'
def retry_if_is_error(instances=ANY, retries=3, wait_time=None, raise_exception=True, on_failed_after_retry_exhausted=None,on_error=None):
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
                    if on_error:
                        on_error(e)
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
                        if on_failed_after_retry_exhausted:
                            on_failed_after_retry_exhausted(e)
                        if raise_exception:
                            raise e

                    print('Retrying')

                    if wait_time is not None:
                        sleep(wait_time)
        return wrapper
    return decorator

def retry_on_db_error(_func: Optional[Callable] = None, *, retries=5, wait_time=5, raise_exception=True):
    def on_failed_after_retry_exhausted(e):
        if os.environ.get("VM"):
            print("Exiting due to SQL Error")
            os.kill(os.getpid(), signal.SIGINT)


    def decorator(func):
        @retry_if_is_error(
            instances=[OperationalError],
            retries=retries,
            wait_time=wait_time,
            raise_exception=raise_exception,
            on_failed_after_retry_exhausted=on_failed_after_retry_exhausted,
            on_error=on_failed_after_retry_exhausted,
        )
        @wraps(func)  # Use functools.wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)

# python -m botasaurus_server.retry_on_db_error
if __name__ == "__main__":
    @retry_on_db_error
    def aa():
        raise Exception()
    aa()