from functools import wraps
from typing import Callable, Optional
from botasaurus.decorator_helpers import retry_if_is_error
from sqlalchemy.exc import OperationalError

def retry_on_db_error(_func: Optional[Callable] = None, *, retries=5, wait_time=5, raise_exception=True):
    def decorator(func):
        @retry_if_is_error(
            instances=[OperationalError],
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

