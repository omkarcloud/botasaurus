import os
from shutil import rmtree
from .env import IS_VM_OR_DOCKER
from .env import IS_PRODUCTION as _IS_PRODUCTION
from .utils import write_file

from .formats import Formats

from .output import fix_excel_filename, write_excel, write_json, write_csv, fix_csv_filename, fix_json_filename

from .decorators_utils import (
    create_directory_if_not_exists,
)
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
        return driver.page_html
    except Exception as e:
        print(f"Error getting page source: {e}")
        return "<html><body><p>Error in getting page source.</p></body></html>"


IS_PRODUCTION = IS_VM_OR_DOCKER or  _IS_PRODUCTION

# Define a global variable to track the first run
first_run = False
def print_running():
    global first_run
    if not first_run:
        first_run = True
        print("Running")
    

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
        import sys
        self._task_queue.put(None)
        thread = self._worker_thread
        try:
            # Must see https://stackoverflow.com/questions/4136632/how-to-kill-a-child-thread-with-ctrlc
            while thread.is_alive():
                thread.join(0.1)
        except KeyboardInterrupt:
            sys.exit(1)
        self._task_queue.join()

        return flatten(self.result_list)



def run_parallel(run, ls, n_workers, use_threads):
    from joblib import Parallel, delayed
    from .thread_with_result import ThreadWithResult
    import sys
    
    if use_threads:
        execute_parallel_tasks = lambda: Parallel(n_jobs=n_workers, backend="threading")(
            delayed(run)(l) for l in ls
        )
    else:
        execute_parallel_tasks = lambda: Parallel(n_jobs=n_workers)(
            delayed(run)(l) for l in ls
        )        

    parallel_thread = ThreadWithResult(target=execute_parallel_tasks, daemon=True)
    parallel_thread.start()
    try:
        while parallel_thread.is_alive():
            parallel_thread.join(0.2)  # time out not to block KeyboardInterrupt
    except KeyboardInterrupt:
        sys.exit(1)

    return parallel_thread.result


class AsyncResult:
    def __init__(self, thread):
        from queue import Queue
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
        import sys
        thread = self._thread
        try:
            while thread.is_alive():
                thread.join(0.1)  # time out not to block KeyboardInterrupt
        except KeyboardInterrupt:
            sys.exit(1)

        self._queue.get()
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


def write_output(output, output_formats, data, result, fn_name):
    written_filenames = []

    if output is None:
        # Output is disabled
        return result

    if callable(output):
        # Dynamic output handling
        output(data, result)
    else:
        # Default format is JSON if not specified
        output_formats = output_formats or ["JSON"]

        if output == "default":
            default_filename = fn_name
        else:
            default_filename = output

        for fm in output_formats:
            if fm == Formats.JSON:
                filename = fix_json_filename(default_filename)
                written_filenames.append(filename)
                write_json(result, filename, False)
            elif fm == Formats.CSV:
                filename = fix_csv_filename(default_filename)
                written_filenames.append(filename)
                write_csv(result, filename, False)
            elif fm == Formats.EXCEL:
                filename = fix_excel_filename(default_filename)
                written_filenames.append(filename)
                write_excel(result, filename, False)

    print_filenames(written_filenames)


def clean_error_logs(error_logs_dir, sort_key):
    # Get list of all folders in the error_logs directory
    folders = [folder for folder in os.listdir(error_logs_dir)]

    # Sort folders based on the timestamp in the folder name
    sorted_folders = sorted(folders, key=sort_key, reverse=True)

    # Keep the recent 10 folders and delete the rest
    folders_to_delete = sorted_folders[10:]
    for folder in folders_to_delete:
        folder_path = os.path.join(error_logs_dir, folder)
        rmtree(folder_path, ignore_errors=True)

def save_error_logs(exception_log, driver):
    from datetime import datetime
    main_error_directory = "error_logs"
    create_directory_if_not_exists(main_error_directory + "/")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
    clean_error_logs("error_logs", lambda x: datetime.strptime(x, '%Y-%m-%d_%H-%M-%S'))
def evaluate_proxy(proxy):
                    if isinstance(proxy, list):
                        import random
                        return  random.choice(proxy)
                    return proxy            