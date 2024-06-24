from functools import wraps
from traceback import print_exc, format_exc
from typing import Any, Callable, Optional, Union, List
from .utils import is_errors_instance
from .beep_utils import beep_input
from .list_utils import flatten

from botasaurus.decorators_common import print_running, write_output, IS_PRODUCTION, AsyncQueueResult, AsyncResult,  run_parallel, save_error_logs
from .dontcache import is_dont_cache

def task(
    _func: Optional[Callable] = None,
    *,
    parallel: Optional[Union[Callable[[Any], int], int]] = None,
    data: Optional[Union[Callable[[], Any], Any]] = None,
    metadata: Optional[Any] = None,
    cache: Union[bool, str] = False,  
    beep: bool = False,
    run_async: bool = False,
    async_queue: bool = False,
    close_on_crash: bool = False,
    output: Optional[Union[str, Callable]] = "default",
    output_formats: Optional[List[str]] = None,
    raise_exception: bool = False,
    must_raise_exceptions: Optional[List[Any]] = None,
    max_retry: Optional[int] = None,
    retry_wait: Optional[int] = None,
    create_error_logs: bool = True,
) -> Callable:
    def decorator_requests(func: Callable) -> Callable:
        if not hasattr(func, '_scraper_type'):
            func._scraper_type = "task"

        @wraps(func)
        def wrapper_requests(*args, **kwargs) -> Any:
            print_running()

            nonlocal parallel, data, cache, beep, run_async, async_queue, metadata
            nonlocal close_on_crash, output, output_formats, max_retry, retry_wait, must_raise_exceptions, raise_exception, create_error_logs

            parallel = kwargs.get("parallel", parallel)
            data = kwargs.get("data", data)
            cache = kwargs.get("cache", cache)
            beep = kwargs.get("beep", beep)
            run_async = kwargs.get("run_async", run_async)
            metadata = kwargs.get("metadata", metadata)
            async_queue = kwargs.get("async_queue", async_queue)
            close_on_crash = kwargs.get("close_on_crash", close_on_crash)
            output = kwargs.get("output", output)
            output_formats = kwargs.get("output_formats", output_formats)
            max_retry = kwargs.get("max_retry", max_retry)
            retry_wait = kwargs.get("retry_wait", retry_wait)
            # A Special Option passed by botasaurus server which prevents caching at database level
            return_dont_cache_as_is = kwargs.get("return_dont_cache_as_is", False)
            must_raise_exceptions = kwargs.get(
                "must_raise_exceptions", must_raise_exceptions
            )
            create_error_logs = kwargs.get("create_error_logs", create_error_logs)

            raise_exception = kwargs.get("raise_exception", raise_exception)

            fn_name = func.__name__

            if cache:
                from .cache import Cache,_get,_has,_get_cache_path,_create_cache_directory_if_not_exists, _put,_remove
                _create_cache_directory_if_not_exists(func)

            def run_task(
                data,
                is_retry,
                retry_attempt,
            ) -> Any:
                if cache is True:
                    path = _get_cache_path(func, data)
                    if _has(path):
                        return _get(path)
                elif cache == 'REFRESH' :
                    path = _get_cache_path(func, data)
                    
                result = None
                try:
                    if "metadata" in kwargs or metadata is not None:
                        result = func(data, metadata)
                    else:
                        result = func( data)
                    if cache is True or cache == 'REFRESH' :
                        if is_dont_cache(result):
                            _remove(path)
                        else:
                            _put(result, path)

                    if is_dont_cache(result):
                        if not return_dont_cache_as_is:
                            result = result.data
                    return result
                except Exception as error:
                    if isinstance(error, KeyboardInterrupt):
                        raise  # Re-raise the KeyboardInterrupt to stop execution

                    if (
                        must_raise_exceptions
                        and is_errors_instance(must_raise_exceptions, error)[0]
                    ):
                        if create_error_logs:
                            save_error_logs(format_exc(), None)
                        raise

                    if max_retry is not None and (max_retry) > (retry_attempt):
                        print_exc()
                        if retry_wait:
                            from time import sleep
                            print("Waiting for " + str(retry_wait) + " seconds")
                            sleep(retry_wait)
                        return run_task(data, True, retry_attempt + 1)

                    if not raise_exception:
                        print_exc()

                    print("Task failed for input:", data)
                    if create_error_logs:
                        save_error_logs(format_exc(), None)

                    
                    if not IS_PRODUCTION:
                        if not close_on_crash:
                            beep_input(
                                "We've paused the browser to help you debug. Press 'Enter' to close.",
                                beep,
                            )

                    

                    if raise_exception:
                        raise error

                    return result

            number_of_workers = parallel() if callable(parallel) else parallel

            if number_of_workers is not None and not isinstance(number_of_workers, int):
                raise ValueError("parallel Option must be a number or None")

            used_data = args[0] if len(args) > 0 else data
            used_data = used_data() if callable(used_data) else used_data
            orginal_data = used_data

            return_first = False
            if type(used_data) is not list:
                return_first = True
                used_data = [used_data]

            result = []

            has_number_of_workers = number_of_workers is not None and not (
                number_of_workers == False
            )

            if not has_number_of_workers or number_of_workers <= 1:
                n = 1
            else:
                n = min(len(used_data), int(number_of_workers))

            if n <= 1:
                for index in range(len(used_data)):
                    data_item = used_data[index]
                    current_result = run_task(data_item, False, 0)
                    result.append(current_result)
            else:

                def run(data_item):
                    current_result = run_task(data_item, False, 0)
                    result.append(current_result)

                    return current_result

                if callable(parallel):
                    print(f"Running {n} Requests in Parallel")

                result = run_parallel(run, used_data, n, True)


            if return_first:
                if not async_queue:
                    write_output(
                        output, output_formats, orginal_data, result[0], fn_name
                    )
                return result[0]
            else:
                if not async_queue:
                    write_output(output, output_formats, orginal_data, result, fn_name)

                return result

        def close():
            # Stub to not cause errors if user accidentatly changes decorator and calls it.
            pass

        wrapper_requests.close = close
        if run_async and async_queue:
            raise ValueError(
                "The options 'run_async' and 'async_queue' cannot be applied at the same time. Please set only one of them to True."
            )

        if run_async:

            @wraps(func)
            def async_wrapper(*args, **kwargs):
                from threading import Thread
                
                def thread_target():
                    result = wrapper_requests(*args, **kwargs)
                    async_result.set_result(result)

                thread = Thread(target=thread_target, daemon=True)
                thread.start()
                async_result = AsyncResult(thread)
                async_wrapper.close = wrapper_requests.close
                return async_result

            return async_wrapper

        elif async_queue:

            @wraps(func)
            def async_wrapper(*args, **wrapper_kwargs):
                from queue import Queue
                from threading import Thread
                if args:
                  raise ValueError('When using "async_queue", data must be passed via ".put".')
   
                task_queue = Queue()
                result_list = []
                orginal_data = []

                def _worker():
                    while True:
                        task = task_queue.get()

                        if task is None:
                            write_output(
                                output,
                                output_formats,
                                orginal_data,
                                flatten(result_list),
                                func.__name__,
                            )
                            task_queue.task_done()
                            break

                        args, kwargs = task
                        merged_kwargs = {
                            **wrapper_kwargs,
                            **kwargs,
                        }  # Merge wrapper_kwargs with kwargs

                        if isinstance(args[0], list):
                            orginal_data.extend(args[0])
                        else:
                            orginal_data.append(args[0])

                        result = wrapper_requests(*args, **merged_kwargs)

                        if isinstance(args[0], list):
                            result_list.extend(result)
                        else:
                            result_list.append(result)

                        task_queue.task_done()

                worker_thread = Thread(target=_worker, daemon=True)

                worker_thread.start()
                async_wrapper.close = wrapper_requests.close
                return AsyncQueueResult(worker_thread, task_queue, result_list)

            return async_wrapper

        return wrapper_requests

    if _func is None:
        return decorator_requests
    else:
        return decorator_requests(_func)
