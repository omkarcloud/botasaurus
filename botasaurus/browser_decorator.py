from functools import wraps
from traceback import print_exc, format_exc
from typing import Any, Callable, Optional, Union, List
from botasaurus.decorators_common import evaluate_proxy, print_running, write_output, IS_PRODUCTION, AsyncQueueResult, AsyncResult,  run_parallel, save_error_logs
from .utils import is_errors_instance
from .list_utils import flatten
from .dontcache import is_dont_cache
from botasaurus_driver.driver import Driver

def close_driver(driver: Driver):
            try:
                driver.close()
            except Exception as e:
                raise

def close_driver_pool(pool: list):
            if len(pool) == 1:
                close_driver(pool[0])
                while pool:
                    pool.pop()
            elif len(pool) > 0:
                while pool:
                    close_driver(pool.pop())

def browser(
    _func: Optional[Callable] = None,
    *,
    parallel: Optional[Union[Callable[[Any], int], int]] = None,
    data: Optional[Union[Callable[[], Any], Any]] = None,
    metadata: Optional[Any] = None,
    cache: Union[bool, str] = False,  
    block_images: bool = False,
    block_images_and_css: bool = False,
    window_size: Optional[Union[Callable[[Any], str], str]] = None,
    tiny_profile: bool = False,
    wait_for_complete_page_load: bool = True,
    add_arguments: Optional[Union[List[str], Callable[[Any, List[str]], None]]] = None,
    extensions: Optional[Union[List[Any], Callable[[Any], List[Any]]]] = None,
    lang: Optional[Union[Callable[[Any], str], str]] = None,
    headless: Optional[Union[Callable[[Any], bool], bool]] = False,
    beep: bool = False,
    close_on_crash: bool = False,
    async_queue: bool = False,
    run_async: bool = False,
    profile: Optional[Union[Callable[[Any], str], str]] = None,
    proxy: Optional[Union[Callable[[Any], str], str]] = None,
    user_agent: Optional[Union[Callable[[Any], str], str]] = None,
    reuse_driver: bool = False,
    output: Optional[Union[str, Callable]] = "default",
    output_formats: Optional[List[str]] = None,
    raise_exception: bool = False,
    must_raise_exceptions: Optional[List[Any]] = None,
    max_retry: Optional[int] = None,
    retry_wait: Optional[int] = None,
    create_error_logs: bool = True,
    create_driver: Optional[Callable] = None,
) -> Callable:
    def decorator_browser(func: Callable) -> Callable:
        if not hasattr(func, '_scraper_type'):
            func._scraper_type = "browser"

        url = None

        @wraps(func)
        def wrapper_browser(*args, **kwargs) -> Any:
            print_running()

            nonlocal parallel, data, cache, block_images_and_css, block_images, window_size, metadata, add_arguments, extensions
            nonlocal tiny_profile, wait_for_complete_page_load, lang, headless, beep
            nonlocal close_on_crash, async_queue, run_async, profile
            nonlocal proxy, user_agent, reuse_driver, raise_exception, must_raise_exceptions

            nonlocal output, output_formats, max_retry, retry_wait, create_driver, create_error_logs

            parallel = kwargs.get("parallel", parallel)
            data = kwargs.get("data", data)
            cache = kwargs.get("cache", cache)
            block_images = kwargs.get("block_images", block_images)
            block_images_and_css = kwargs.get("block_images_and_css", block_images_and_css)
            add_arguments = kwargs.get("add_arguments", add_arguments)
            extensions = kwargs.get("extensions", extensions)
            window_size = kwargs.get("window_size", window_size)

            metadata = kwargs.get("metadata", metadata)
            tiny_profile = kwargs.get("tiny_profile", tiny_profile)
            wait_for_complete_page_load = kwargs.get("wait_for_complete_page_load", wait_for_complete_page_load)
            lang = kwargs.get("lang", lang)
            headless = kwargs.get("headless", headless)
            beep = kwargs.get("beep", beep)
            close_on_crash = kwargs.get("close_on_crash", close_on_crash)
            async_queue = kwargs.get("async_queue", async_queue)
            run_async = kwargs.get("run_async", run_async)
            profile = kwargs.get("profile", profile)
            proxy = kwargs.get("proxy", proxy)
            user_agent = kwargs.get("user_agent", user_agent)
            reuse_driver = kwargs.get("reuse_driver", reuse_driver)
            dont_close_driver = reuse_driver
            output = kwargs.get("output", output)
            output_formats = kwargs.get("output_formats", output_formats)
            max_retry = kwargs.get("max_retry", max_retry)
            retry_wait = kwargs.get("retry_wait", retry_wait)
            # A Special Option passed by botasaurus server which prevents caching at database level
            return_dont_cache_as_is = kwargs.get("return_dont_cache_as_is", False)
            create_error_logs = kwargs.get("create_error_logs", create_error_logs)

            raise_exception = kwargs.get("raise_exception", raise_exception)
            create_driver = kwargs.get("create_driver", create_driver)

            fn_name = func.__name__

            if cache:
                from .cache import Cache,_get,_has,_get_cache_path,_create_cache_directory_if_not_exists, _put,_remove

                _create_cache_directory_if_not_exists(func)
            if isinstance(proxy, list):
                from itertools import cycle       
                cycled_proxy = cycle(proxy)         
            else:
                cycled_proxy = None

            # # Pool to hold reusable drivers
            _driver_pool = wrapper_browser._driver_pool if dont_close_driver else []

            def run_task(data, is_retry, retry_attempt, retry_driver=None) -> Any:
                if cache is True:
                    path = _get_cache_path(func, data)
                    if _has(path):
                        return _get(path)
                elif cache == 'REFRESH' :
                    path = _get_cache_path(func, data)
                    

                evaluated_window_size = (
                    window_size(data) if callable(window_size) else window_size
                )
                evaluated_user_agent = (
                    user_agent(data) if callable(user_agent) else user_agent
                )
                if cycled_proxy:
                    evaluated_proxy = next(cycled_proxy)
                else:
                    evaluated_proxy = evaluate_proxy(proxy(data) if callable(proxy) else proxy)
                evaluated_profile = profile(data) if callable(profile) else profile
                evaluated_lang = lang(data) if callable(lang) else lang
                evaluated_headless = headless(data) if callable(headless) else headless
                evaluated_extensions = extensions(data) if callable(extensions) else extensions

                if evaluated_profile is not None:
                    evaluated_profile = str(evaluated_profile)
                if retry_driver is not None:
                    driver = retry_driver
                elif reuse_driver and len(_driver_pool) > 0:
                    driver = _driver_pool.pop()
                else:
                    if callable(add_arguments):
                        args  = add_arguments(data)
                        if not isinstance(args, list):
                            raise Exception("add_arguments must return a list of arguments")
                    else:
                        args = add_arguments

                    driver = Driver(headless=evaluated_headless, proxy=evaluated_proxy, profile=evaluated_profile, tiny_profile=tiny_profile, block_images=block_images, block_images_and_css=block_images_and_css, wait_for_complete_page_load=wait_for_complete_page_load, extensions=evaluated_extensions, arguments=args, user_agent=evaluated_user_agent, window_size=evaluated_window_size, lang=evaluated_lang, beep=beep)

                result = None
                try:
                    if max_retry is not None:
                            driver.config.is_last_retry = not (
                                (max_retry) > (retry_attempt)
                            )
                            driver.config.retry_attempt = retry_attempt
                            driver.config.is_retry = retry_attempt != 0
                    # if evaluated_profile is not None:
                    if "metadata" in kwargs or metadata is not None:
                        result = func(driver, data, metadata)
                    else:
                        result = func(driver, data)
                    if reuse_driver:
                        driver.config.is_new = False
                        _driver_pool.append(driver)  # Add back to the pool for reuse
                    else:
                        close_driver(driver)

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
                        close_driver_pool(_driver_pool)
                        raise  # Re-raise the KeyboardInterrupt to stop execution

                    if (
                        must_raise_exceptions
                        and is_errors_instance(must_raise_exceptions, error)[0]
                    ):
                        if create_error_logs:
                            save_error_logs(format_exc(), driver)
                        close_driver(driver)
                        raise

                    if max_retry is not None and (max_retry) > (retry_attempt):
                        print_exc()
                        close_driver(driver)
                        if retry_wait:
                            from time import sleep
                            print("Waiting for " + str(retry_wait))
                            sleep(retry_wait)
                        return run_task(data, True, retry_attempt + 1)

                    if not raise_exception:
                        print_exc()

                    print("Task failed for input:", data)
                    if create_error_logs:
                        save_error_logs(format_exc(), driver)
                    
                    if not close_on_crash:
                        if not IS_PRODUCTION:
                            if headless:
                                driver.open_in_devtools()
                            driver.prompt("We've paused the browser to help you debug. Press 'Enter' to close.")

                    # if reuse_driver:
                    #     driver.is_new = False
                    #     _driver_pool.append(driver)  # Add back to the pool for reuse
                    # else:
                    close_driver(driver)

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
                    print(f"Running {n} Browsers in Parallel")
                
                result = run_parallel(run, used_data, n, True)

            if not dont_close_driver:
                close_driver_pool(_driver_pool)
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

        wrapper_browser._driver_pool = []

        def close_drivers():
            close_driver_pool(wrapper_browser._driver_pool)

        wrapper_browser.close = close_drivers

        if run_async and async_queue:
            raise ValueError(
                "The options 'run_async' and 'async_queue' cannot be applied at the same time. Please set only one of them to True."
            )

        if run_async:

            @wraps(func)
            def async_wrapper(*args, **kwargs):
                from threading import Thread
                def thread_target():
                    result = wrapper_browser(*args, **kwargs)
                    async_result.set_result(result)

                thread = Thread(target=thread_target, daemon=True)
                thread.start()
                async_result = AsyncResult(thread)
                return async_result

            async_wrapper._driver_pool = wrapper_browser._driver_pool
            async_wrapper.close = wrapper_browser.close
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

                        result = wrapper_browser(*args, **merged_kwargs)

                        if isinstance(args[0], list):
                            result_list.extend(result)
                        else:
                            result_list.append(result)

                        task_queue.task_done()

                worker_thread = Thread(target=_worker, daemon=True)

                worker_thread.start()

                return AsyncQueueResult(worker_thread, task_queue, result_list)

            async_wrapper._driver_pool = wrapper_browser._driver_pool
            async_wrapper.close = wrapper_browser.close
            return async_wrapper

        return wrapper_browser

    if _func is None:
        return decorator_browser
    else:
        return decorator_browser(_func)
