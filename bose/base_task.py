import os
import traceback
from bose.create_driver import BrowserConfig, create_driver
from bose.drivers.boss_driver import BossDriver
from bose.utils import relative_path, merge_dicts_in_one_dict, write_file, write_html, write_json
from .local_storage import LocalStorage
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

class BaseTask():
    def __init__(self):
        pass

    browser_config = BrowserConfig()

    def get_browser_config(self):
        return self.browser_config

    def create_driver(self, config: BrowserConfig):
        return create_driver(config)
    
    def begin_task(self):
        def create_task_directory(task_path):
            path =  relative_path(task_path, 0)
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                pass

        def run_task(is_retry, retry_attempt):
            task = TaskInfo()
            print('Task Started')
            task.start()
            
            def end_task(driver:BossDriver):
                task.end()
                task.set_ip()
                data = task.data
                driver.save_screenshot()
                
                html_path  = f'{self.task_path}/page.html'
                source = get_page_source_safe(driver)
                write_html(source, html_path)

                data["driver_url"] = get_driver_url_safe(driver)
                
                if is_retry: 
                    data["is_retry"] = is_retry
                    data["retry_attempt"] = retry_attempt

                print("Closing Browser")                
                driver.close()
                print("Closed Browser")                

                task_info_path  = f'{self.task_path}/task_info.json'
                
                if driver._init_data is not None:
                    data = merge_dicts_in_one_dict(data , driver._init_data)
                
                write_json(data , task_info_path)

            count = LocalStorage.get_item('count', 0) + 1
            LocalStorage.set_item('count', count)

            driver = self.create_driver(self.get_browser_config())

            self.task_path = f'tasks/{count}' 
            self.task_id = count

            create_task_directory(self.task_path)
            driver.task_id = self.task_id
            driver.task_path = self.task_path


            try:
                self.run(driver)
                end_task(driver)
                print('Task Completed!')
            except RetryException as error:
                end_task(driver)
                print('Task is being Retried!')
                return run_task(True, retry_attempt + 1)
            except Exception as error:
                exception_log = traceback.format_exc()
                traceback.print_exc()
                end_task(driver)

                error_log_path  = f'{self.task_path}/error.log'
                write_file(exception_log, error_log_path)

                print('Task Failed!')

        return run_task(False, 0)

    def run(self, driver: BossDriver):
        pass


class Task(BaseTask):
    def __init__(self):
        pass

    def run(self, driver):
        pass


if __name__ == "__main__":
    t = BaseTask()
