from selenium.common.exceptions import WebDriverException
from functools import wraps
from queue import Queue
from threading import Thread
from traceback import print_exc, format_exc
from typing import Any, Callable, Optional, Union, List
import os
from datetime import datetime

from joblib import Parallel, delayed

from .utils import write_file

from .formats import Formats

from .output import write_json, write_csv, fix_csv_filename, fix_json_filename
from .cache import Cache,  is_dont_cache, _get, _has, _get_cache_path, _create_cache_directory_if_not_exists

from .create_driver_utils import add_about, save_cookies
from . import creators
# import create_driver, create_requests
from .anti_detect_driver import AntiDetectDriver
from .beep_utils import beep_input
from .decorators_utils import create_directories_if_not_exists, create_directory_if_not_exists
from .local_storage import LocalStorage
from .profile import Profile
from .usage import Usage
from .list_utils import flatten

class RetryException(Exception):
    pass

def get_driver_url_safe(driver):
    try:
        return driver.current_url
    except:
        return "Failed to get driver url"

def get_page_source_safe(driver):
    try:
        return driver.page_source
    except Exception as e:
        print(f"Error getting page source: {e}")
        return "<html><body><p>Error in getting page source.</p></body></html>"


IS_PRODUCTION = os.environ.get("ENV") == "production"
create_directories_if_not_exists()

# Define a global variable to track the first run
first_run = True



class AsyncQueueResult:
    def __init__(self, worker_thread, task_queue, result_list):
        self._worker_thread = worker_thread
        self._task_queue = task_queue
        self.result_list = result_list
        self._seen_items = set()

    def get_unique(self, items):
        single_item = False
        if not isinstance(items, list):
            items = [items]
            single_item = True

        new_items = []

        for item in items:
            if isinstance(item, dict):
                item_repr = frozenset(item.items())
            elif isinstance(item, list):
                item_repr = tuple(item)
            elif isinstance(item, set):
                item_repr = frozenset(item)
            else:
                item_repr = item

            if item_repr not in self._seen_items:
                new_items.append(item)
                self._seen_items.add(item_repr)

        return new_items[0] if single_item and new_items else new_items

    def put(self, *args, **kwargs):
        if args:
            unique_args = self.get_unique(args[0])
            args_to_put = (unique_args, *args[1:])
        else:
            args_to_put = ()

        self._task_queue.put([args_to_put, kwargs])

    def get(self):
                    self._task_queue.join()
                    self._task_queue.put(None)
                    self._worker_thread.join()
                    return flatten(self.result_list)

class AsyncResult:
    def __init__(self, thread):
        self._result = None
        self._completed = False
        self._exception = None
        self._queue = Queue()
        self._thread = thread

    def set_result(self, value):
        self._result = value
        self._completed = True
        self._queue.put(True)

    def set_exception(self, exception):
        self._exception = exception
        self._completed = True
        self._queue.put(True)

    def get(self):
        self._queue.get()
        self._thread.join()  # Join the thread after the result is available or an exception occurs
        if self._exception:
            raise self._exception
        return self._result

    def is_completed(self):
        return self._completed


def get_driver_url_safe(driver):
    try:
        return driver.current_url
    except:
        return "Failed to get driver url"

def print_filenames(written_filenames):
    if len(written_filenames) > 0:  # Check if the list is not empty
        print("Written")
        for filename in written_filenames:
            print("    ", filename)

def write_output(output,output_formats, data, result, fn_name):
            written_filenames = []

            if output is None:
                # Output is disabled
                return result
            
            if callable(output):
                # Dynamic output handling
                output(data, result)
            else:
        
                # Default format is JSON if not specified
                output_formats = output_formats or ['JSON']
                
                if output == 'default':
                    default_filename =  fn_name
                else:
                    default_filename =  output

                for fm in output_formats:
                    if fm == Formats.JSON:
                        filename = fix_json_filename(default_filename)
                        written_filenames.append(filename)  
                        write_json(result, filename, False)
                    elif fm == Formats.CSV:
                        filename = fix_csv_filename(default_filename)
                        written_filenames.append(filename)  
                        write_csv(result, filename, False)

            print_filenames(written_filenames)

def save_error_logs(exception_log, driver):
    main_error_directory = "error_logs"
    create_directory_if_not_exists(main_error_directory  + "/")

    timestamp =  datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    error_directory = f"{main_error_directory}/{timestamp}"
    create_directory_if_not_exists(error_directory + "/")

    error_filename = f"{error_directory}/error.log"
    screenshot_filename = f"{error_directory}/screenshot.png"
    page_filename = f"{error_directory}/page.html"

    write_file(exception_log, error_filename)

    if driver is not None:
        source = get_page_source_safe(driver)
        write_file(source, page_filename)

        try:
            driver.save_screenshot(screenshot_filename)
        except Exception as e:
            print(f"Error saving screenshot: {e}")



def browser(
    _func: Optional[Callable] = None, *,
    parallel: Optional[Union[Callable[[Any], int], int]] = None,
    data: Optional[Union[Callable[[], Any], Any]] = None,
    cache: bool = False,
    block_images: bool = False,
    window_size: Optional[Union[Callable[[Any], str], str]] = None,
    tiny_profile: bool = False,
    is_eager: bool = False,
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
    keep_drivers_alive: bool = False,
    output: Optional[Union[str, Callable]] = "default", 
    output_formats: Optional[List[str]] = None,
    max_retry: Optional[int] = None, 
    create_driver :Optional[Callable]=None, 


) -> Callable:
        
    global first_run  # Declare the global variable to modify it
    if first_run:  # Check if it's the first run
        print("Running")  # If so, print "Running"
        first_run = False  # Set the flag to False so it doesn't run again

    def decorator_browser(func: Callable) -> Callable:




        def close_driver(driver:AntiDetectDriver):
            if tiny_profile:
            #   if driver.about.profile:
                save_cookies(driver, driver.about.profile)
            # Maybe Fixes the Chrome Processes Hanging Issue. Not Sure
            # nonlocal url
            # if url is None:
            #     url = get_driver_url_safe(driver)
            
            try:
                driver.close() 
                driver.quit()
            except WebDriverException as e:
                if "not connected to DevTools" in str(e):
                    print("Unable to close driver due to network issues")
                    # This error occurs due to connectivty issues
                    pass
                else:
                    raise
                
        def close_driver_pool(pool:list):
                if len(pool) == 1:
                    close_driver(pool[0])
                    while pool:
                        pool.pop()
                elif len(pool) > 0:
                    Parallel(n_jobs=len(pool), backend="threading")(delayed(close_driver)(l) for l in pool)
                    while pool:
                        pool.pop()


        url = None

        def can_put_url():
            nonlocal url
            return url is None

        def set_url(s):
            nonlocal url
            if s is not None:
                url = s

        def get_url():
            nonlocal url
            return url
            
        @wraps(func)
        def wrapper_browser(*args, **kwargs) -> Any:

            nonlocal parallel, data, cache, block_images, window_size
            nonlocal tiny_profile, is_eager, lang, headless, beep
            nonlocal close_on_crash, async_queue, run_async, profile
            nonlocal proxy, user_agent, reuse_driver, keep_drivers_alive
            nonlocal output, output_formats, max_retry, create_driver

            parallel = kwargs.get('parallel', parallel)
            data = kwargs.get('data', data)
            cache = kwargs.get('cache', cache)
            block_images = kwargs.get('block_images', block_images)
            window_size = kwargs.get('window_size', window_size)
            tiny_profile = kwargs.get('tiny_profile', tiny_profile)
            is_eager = kwargs.get('is_eager', is_eager)
            lang = kwargs.get('lang', lang)
            headless = kwargs.get('headless', headless)
            beep = kwargs.get('beep', beep)
            close_on_crash = kwargs.get('close_on_crash', close_on_crash)
            async_queue = kwargs.get('async_queue', async_queue)
            run_async = kwargs.get('run_async', run_async)
            profile = kwargs.get('profile', profile)
            proxy = kwargs.get('proxy', proxy)
            user_agent = kwargs.get('user_agent', user_agent)
            reuse_driver = kwargs.get('reuse_driver', reuse_driver)
            keep_drivers_alive = kwargs.get('keep_drivers_alive', keep_drivers_alive)
            output = kwargs.get('output', output)
            output_formats = kwargs.get('output_formats', output_formats)
            max_retry = kwargs.get('max_retry', max_retry)
            create_driver = kwargs.get('create_driver', create_driver)


            fn_name = func.__name__
            
            _create_cache_directory_if_not_exists(func)
            
            
            count = LocalStorage.get_item('count', 0) + 1
            LocalStorage.set_item('count', count)
            # 

            # # Pool to hold reusable drivers
            _driver_pool =  wrapper_browser._driver_pool if keep_drivers_alive  else []


            def run_task(data, is_retry, retry_attempt, retry_driver = None) -> Any:
                if cache:
                    path = _get_cache_path(func, data)
                    if _has(path):
                        return _get(path)

                evaluated_window_size = window_size(data) if callable(window_size) else window_size
                evaluated_user_agent = user_agent(data) if callable(user_agent) else user_agent
                evaluated_proxy = proxy(data) if callable(proxy) else proxy
                evaluated_profile = profile(data) if callable(profile) else profile
                evaluated_lang = lang(data) if callable(lang) else lang
                evaluated_headless = headless(data) if callable(headless) else headless


                if evaluated_profile is not None:
                    evaluated_profile = str(evaluated_profile)

                if retry_driver is not None:
                    driver = retry_driver
                elif reuse_driver and len(_driver_pool) > 0:
                    driver = _driver_pool.pop()
                else:
                    if create_driver:
                        driver = create_driver(data)
                        add_about(tiny_profile, proxy, lang, beep, {}, driver)
                    else:
                        driver = creators.create_driver(tiny_profile, evaluated_profile, evaluated_window_size, evaluated_user_agent, evaluated_proxy, is_eager, evaluated_headless, evaluated_lang, block_images, beep)
                result = None
                try:
                    # if evaluated_profile is not None:
                    Profile.profile = evaluated_profile

                    result = func(driver, data)

                    if can_put_url():
                        set_url(get_driver_url_safe(driver))
                    if reuse_driver:
                        driver.about.is_new = False
                        _driver_pool.append(driver)  # Add back to the pool for reuse
                    else:
                        close_driver(driver)

                    if cache:
                        if is_dont_cache(result):
                            pass
                        else:
                            Cache.put(func, data, result)
                    
                    if is_dont_cache(result):
                        result = result.data

                    return result
                except Exception as error:
                    if isinstance(error, KeyboardInterrupt):
                        close_driver_pool(_driver_pool)
                        raise  # Re-raise the KeyboardInterrupt to stop execution

                    if max_retry is not None and (max_retry) > (retry_attempt):
                            return run_task(data, True, retry_attempt + 1)

                    exception_log = format_exc()
                    print_exc()
                    save_error_logs(exception_log, driver)
                    
                    if not headless:
                        if not IS_PRODUCTION:
                            if not close_on_crash:
                                driver.prompt("We've paused the browser to help you debug. Press 'Enter' to close.")

                    if reuse_driver:
                        driver.is_new = False
                        _driver_pool.append(driver)  # Add back to the pool for reuse
                    else:
                        close_driver(driver)

                    print('Task failed with data:', data)
                    return result

            
            number_of_workers = parallel() if callable(parallel) else parallel
            
            if number_of_workers is not None and not isinstance(number_of_workers, int):
                raise ValueError("parallel Option must be a number or None")

            used_data =  args[0] if len(args) > 0 else data
            used_data = used_data() if callable(used_data) else used_data
            orginal_data = used_data
            
            return_first = False
            if type(used_data) is not list:
                return_first = True
                used_data = [used_data]

            result = []
            has_number_of_workers = number_of_workers is not None and not (number_of_workers == False)
            
            if not has_number_of_workers or number_of_workers <=1: 
                n = 1
            else:
                n = min(len(used_data), int(number_of_workers))

            prevprofile = Profile.profile
            if n <= 1:
                for index in range(len(used_data)):
                    data_item = used_data[index]
                    current_result = run_task(data_item, False, 0)
                    Profile.profile = prevprofile
                    result.append(current_result)
            else:
                def run(data_item):
                    current_result = run_task(data_item, False, 0)
                    Profile.profile = prevprofile
                    result.append(current_result)
                                  
                    return current_result

                if callable(parallel):
                    print(f"Running {n} Browsers in Parallel")

                result = (Parallel(n_jobs=n, backend="threading")(delayed(run)(l) for l in used_data))
            
            if not keep_drivers_alive:
                close_driver_pool(_driver_pool)

            # result = flatten(result)
            if not async_queue:
                Usage.put(fn_name, url)
            if return_first:
                if not async_queue:
                    write_output(output,output_formats, orginal_data, result[0], fn_name)
                return result[0]
            else: 
                
                if not async_queue:
                    write_output(output,output_formats, orginal_data, result, fn_name)
                
                return result
        
        wrapper_browser._driver_pool = []
        
        def close_drivers():
                close_driver_pool(wrapper_browser._driver_pool)
            
        wrapper_browser.close = close_drivers

        if run_async and async_queue:
            raise ValueError("The options 'run_async' and 'async_queue' cannot be applied at the same time. Please set only one of them to True.")

        if run_async:
            @wraps(func)
            def async_wrapper(*args, **kwargs):
                def thread_target():
                        result = wrapper_browser(*args, **kwargs)
                        async_result.set_result(result)

                thread = Thread(target=thread_target, daemon = True)
                thread.start()
                async_result = AsyncResult(thread)
                return async_result
            async_wrapper._driver_pool  = wrapper_browser._driver_pool
            async_wrapper.close  = wrapper_browser.close
            return async_wrapper
        elif async_queue:
            @wraps(func)
            def async_wrapper():
                task_queue = Queue()
                result_list = []
                orginal_data = []

                
                def _worker():
                    while True:
                        task = task_queue.get()
                        
                        if task is None:
                            Usage.put(func.__name__, get_url())

                            write_output(output,output_formats, orginal_data, flatten(result_list), func.__name__)
                            break

                        args = task[0]
                        kwargs = task[1]
                        # print(args)
                        orginal_data.append(args[0])
                        
                        result = wrapper_browser(*args, **kwargs)
                        result_list.extend(result)
                        task_queue.task_done()
                
                worker_thread = Thread(target=_worker, daemon = True )

                worker_thread.start()

                return AsyncQueueResult(worker_thread, task_queue, result_list)

            async_wrapper._driver_pool  = wrapper_browser._driver_pool
            async_wrapper.close  = wrapper_browser.close
            return async_wrapper

        return wrapper_browser

    if _func is None:
        return decorator_browser
    else:
        return decorator_browser(_func)




def request(
    _func: Optional[Callable] = None, *,
    parallel: Optional[Union[Callable[[Any], int], int]] = None,
    data: Optional[Union[Callable[[], Any], Any]] = None,
    cache: bool = False,
    beep: bool = False,
    run_async: bool = False,
    async_queue: bool = False,
    proxy: Optional[Union[Callable[[Any], str], str]] = None,
    close_on_crash: bool = False,      
    output: Optional[Union[str, Callable]] = "default", 
    output_formats: Optional[List[str]] = None, 
    max_retry: Optional[int] = None
)-> Callable:
    global first_run  # Declare the global variable to modify it
    if first_run:  # Check if it's the first run
        print("Running")  # If so, print "Running"
        first_run = False  # Set the flag to False so it doesn't run again

    def decorator_requests(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_requests(*args, **kwargs) -> Any:
            nonlocal parallel, data, cache, beep, run_async, async_queue
            nonlocal proxy, close_on_crash, output, output_formats, max_retry

            parallel = kwargs.get('parallel', parallel)
            data = kwargs.get('data', data)
            cache = kwargs.get('cache', cache)
            beep = kwargs.get('beep', beep)
            run_async = kwargs.get('run_async', run_async)
            async_queue = kwargs.get('async_queue', async_queue)
            proxy = kwargs.get('proxy', proxy)
            close_on_crash = kwargs.get('close_on_crash', close_on_crash)
            output = kwargs.get('output', output)
            output_formats = kwargs.get('output_formats', output_formats)
            max_retry = kwargs.get('max_retry', max_retry)

            fn_name = func.__name__
            _create_cache_directory_if_not_exists(func)
            
            count = LocalStorage.get_item('count', 0) + 1
            LocalStorage.set_item('count', count)

            def run_task(data, is_retry, retry_attempt, ) -> Any:
                        
                if cache:
                    path = _get_cache_path(func, data)
                    if _has(path):
                        return _get(path)


                evaluated_proxy = proxy(data) if callable(proxy) else proxy

                reqs = creators.create_requests(evaluated_proxy)

                result = None
                try:
                    result = func(reqs, data)
                    if cache:
                        if is_dont_cache(result):
                            pass
                        else:
                            Cache.put(func, data, result)
                    
                    if is_dont_cache(result):
                        result = result.data

                    return result
                except Exception as error:
                    if isinstance(error, KeyboardInterrupt):
                        raise  # Re-raise the KeyboardInterrupt to stop execution
                    
                    if max_retry is not None and (max_retry)> (retry_attempt):
                            return run_task(data, True, retry_attempt + 1)

                    exception_log = format_exc()
                    print_exc()
                    save_error_logs(exception_log, None)
                    
                    if not IS_PRODUCTION:
                        if not close_on_crash:
                            beep_input("We've paused the browser to help you debug. Press 'Enter' to close.", beep)

                    print(f'Task Failed!')
                    return result


            number_of_workers = parallel() if callable(parallel) else parallel

            if number_of_workers is not None and not isinstance(number_of_workers, int):
                raise ValueError("parallel Option must be a number or None")


            used_data =  args[0] if len(args) > 0 else data
            used_data = used_data() if callable(used_data) else used_data
            orginal_data = used_data


            return_first = False
            if type(used_data) is not list:
                return_first = True
                used_data = [used_data]

            result = []

            has_number_of_workers = number_of_workers is not None and not (number_of_workers == False)
            
            if not has_number_of_workers or number_of_workers <=1: 
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

                result = (Parallel(n_jobs=n, backend="threading")(delayed(run)(l) for l in used_data))
            

            # result = flatten(result)
            if not async_queue:
                Usage.put(fn_name, None)

            

            if return_first:
                if not async_queue:
                    write_output(output,output_formats, orginal_data, result[0], fn_name)
                return result[0]
            else: 
                
                if not async_queue:
                    write_output(output,output_formats, orginal_data, result, fn_name)
                
                return result

        def close():
            # Stub to not cause errors if user accidentatly changes decorator and calls it.
            pass
        wrapper_requests.close  = close
        if run_async and async_queue:
            raise ValueError("The options 'run_async' and 'async_queue' cannot be applied at the same time. Please set only one of them to True.")

        if run_async:
            @wraps(func)
            def async_wrapper(*args, **kwargs):
                def thread_target():
                        result = wrapper_requests(*args, **kwargs)
                        async_result.set_result(result)

                thread = Thread(target=thread_target, daemon = True)
                thread.start()
                async_result = AsyncResult(thread)
                async_wrapper.close  = wrapper_requests.close
                return async_result
            return async_wrapper
        
        elif async_queue:
            @wraps(func)
            def async_wrapper():
                task_queue = Queue()
                result_list = []
                orginal_data = []

                def _worker():
                    while True:
                        task = task_queue.get()
                        
                        if task is None:
                            Usage.put(func.__name__, None)
                            # Thread Finished
                            write_output(output,output_formats, orginal_data, flatten(result_list), func.__name__)
                            break

                        args = task[0]
                        kwargs = task[1]
                        
                        orginal_data.append(args[0])

                        result = wrapper_requests(*args, **kwargs)
                        result_list.append(result)
                        task_queue.task_done()
                
                worker_thread = Thread(target=_worker, daemon = True )

                worker_thread.start()
                async_wrapper.close  = wrapper_requests.close
                return AsyncQueueResult(worker_thread, task_queue, result_list)

            return async_wrapper

        return wrapper_requests

    if _func is None:
        return decorator_requests
    else:
        return decorator_requests(_func)