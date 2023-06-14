import os
import traceback
from .create_driver import BrowserConfig, create_driver
from .bose_driver import BoseDriver
from .utils import relative_path, merge_dicts_in_one_dict, write_file, write_html, write_json,get_driver_path
from .local_storage import LocalStorage
from .analytics import Analytics
from .task_info import TaskInfo


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
    except:
        return "Failed to get page_source"


def _download_driver():
    from .download_driver import download_driver
    download_driver()
    
class BaseTask():
    def __init__(self):
        self.task_path = None
        self.task_id = None        


    browser_config = BrowserConfig()

    def get_browser_config(self):
        return self.browser_config

    def create_driver(self, config: BrowserConfig):
        return create_driver(config)
    
    def begin_task(self):
        def create_directories(task_path):

            driver_path =  relative_path(get_driver_path(), 0)
            if not os.path.isfile(driver_path):
                print('Downloading Driver in build/ directory ...')
                _download_driver()

            tasks_path =  relative_path('tasks/', 0)
            if not os.path.exists(tasks_path):
                os.makedirs(tasks_path)

            profiles_path =  relative_path('profiles/', 0)
            if not os.path.exists(profiles_path):
                os.makedirs(profiles_path)

            path =  relative_path(task_path, 0)
            if not os.path.exists(path):
                os.makedirs(path)

        def run_task(is_retry, retry_attempt):
            # print('Launching Task')
            task = TaskInfo()
            
            def close_driver(driver):
                print("Closing Browser")                
                driver.close()
                print("Closed Browser")                


            final_image = "final.png"
            def end_task(driver:BoseDriver):
                task.end()
                task.set_ip()
                data = task.data
                driver.save_screenshot(final_image)
                
                html_path  = f'{self.task_path}/page.html'
                source = get_page_source_safe(driver)
                write_html(source, html_path)

                data["last_url"] = get_driver_url_safe(driver)
                
                if is_retry: 
                    data["is_retry"] = is_retry
                    data["retry_attempt"] = retry_attempt


                task_info_path  = f'{self.task_path}/task_info.json'
                
                if driver._init_data is not None:
                    data = merge_dicts_in_one_dict(data , driver._init_data)
                
                write_json(data , task_info_path)
                Analytics.send_tracking_data()
            count = LocalStorage.get_item('count', 0) + 1
            LocalStorage.set_item('count', count)

            self.task_path = f'tasks/{count}' 
            self.task_id = count

            create_directories(self.task_path)
            print('Task Started')
            task.start()
            config = self.get_browser_config()
            driver = self.create_driver(config)

            driver.task_id = self.task_id
            driver.task_path = self.task_path

            final_image_path = f'{self.task_path}/{final_image}'
            try:
                self.run(driver)
                end_task(driver)
                close_driver(driver)
                print(f'Task Completed! View Final Screenshot at {final_image_path}')
            except RetryException as error:
                end_task(driver)
                close_driver(driver)
                print('Task is being Retried!')
                return run_task(True, retry_attempt + 1)
            except Exception as error:
                exception_log = traceback.format_exc()
                traceback.print_exc()
                end_task(driver)
                
                error_log_path  = f'{self.task_path}/error.log'
                write_file(exception_log, error_log_path)

                IS_PRODUCTION = os.environ.get("ENV") == "production"

                if not IS_PRODUCTION:
                    if not config.close_on_crash:
                        driver.wait_for_enter("Press Enter To Close Browser")
                    
                close_driver(driver)

                print(f'Task Failed! View Final Screenshot at {final_image_path}')

        return run_task(False, 0)

    def run(self, driver: BoseDriver):
        pass


class Task(BaseTask):
    def __init__(self):
        pass

    def run(self, driver):
        pass


if __name__ == "__main__":
    t = BaseTask()
