import os
import traceback
from .beep_utils import beep_input

from .profile import Profile

from .schedule_utils import ScheduleUtils
from .create_driver import BrowserConfig, create_driver
from .bose_driver import BoseDriver
from .utils import relative_path,read_json,  merge_dicts_in_one_dict, write_file, write_html, write_json,get_driver_path
from .local_storage import LocalStorage
from .analytics import Analytics
from .task_info import TaskInfo
from .task_config import TaskConfig

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
    

def get_current_profile_path(config: BrowserConfig): 
    profiles_path = f'profiles/{config.profile}/'
    # profiles_path =  relative_path(path, 0)
    return profiles_path
    
def save_cookies(driver, config):
    current_profile_data = get_current_profile_path(config) + 'profile.json'
    current_profile_data_path =  relative_path(current_profile_data, 0)

    driver.execute_cdp_cmd('Network.enable', {})
    cookies = (driver.execute_cdp_cmd('Network.getAllCookies', {}))
    driver.execute_cdp_cmd('Network.disable', {})

    if type(cookies) is not list:
         cookies = cookies.get('cookies')
    write_json(cookies, current_profile_data_path)

def load_cookies(driver: BoseDriver, config):
    current_profile = get_current_profile_path(config)
    current_profile_path =  relative_path(current_profile, 0)

    if not os.path.exists(current_profile_path):
        os.makedirs(current_profile_path)
    

    current_profile_data = get_current_profile_path(config) + 'profile.json'
    current_profile_data_path =  relative_path(current_profile_data, 0)

    if not os.path.isfile(current_profile_data_path):
        return

    cookies = read_json(current_profile_data_path)
    # Enables network tracking so we may use Network.setCookie method
    driver.execute_cdp_cmd('Network.enable', {})
    # Iterate through pickle dict and add all the cookies
    for cookie in cookies:
        # Fix issue Chrome exports 'expiry' key but expects 'expire' on import
        if 'expiry' in cookie:
            cookie['expires'] = cookie['expiry']
            del cookie['expiry']
        # Replace domain 'apple.com' with 'microsoft.com' cookies
        cookie['domain'] = cookie['domain'].replace('apple.com', 'microsoft.com')
        # Set the actual cookie
        driver.execute_cdp_cmd('Network.setCookie', cookie)
        
    driver.execute_cdp_cmd('Network.disable', {})


class BaseTask():
    def __init__(self):
        self.task_path = None
        self.task_id = None        


    task_config = TaskConfig()

    def get_task_config(self):
        return self.task_config

    browser_config = BrowserConfig()

    def get_browser_config(self, data):
        return self.browser_config


    data = [None]
    def get_data(self):
        return self.data


    def schedule(self, data):
        """
            Seconds delay between each run
        """
        return ScheduleUtils.no_delay(data)


    def create_driver(self, config: BrowserConfig):
        return create_driver(config)
    
    def begin_task(self, data, task_config:TaskConfig):
        def create_directories(task_path):

            driver_path =  relative_path(get_driver_path(), 0)
            if not os.path.isfile(driver_path):
                print('Downloading Driver in build/ directory ...')
                _download_driver()

            tasks_path =  relative_path('tasks/', 0)
            if not os.path.exists(tasks_path):
                os.makedirs(tasks_path)

            output_path =  relative_path('output/', 0)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            profiles_path =  relative_path('profiles/', 0)
            if not os.path.exists(profiles_path):
                os.makedirs(profiles_path)

            path =  relative_path(task_path, 0)
            if not os.path.exists(path):
                os.makedirs(path)

        def run_task(is_retry, retry_attempt):
            # print('Launching Task')
            task = TaskInfo()
            task_name = self.__class__.__name__
            TaskInfo.set_task_name(task_name)

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
                Analytics.send_tracking_data(task_name)
            count = LocalStorage.get_item('count', 0) + 1
            LocalStorage.set_item('count', count)

            self.task_path = f'tasks/{count}' 
            self.task_id = count

            create_directories(self.task_path)
            
            task.start()
            config = self.get_browser_config(data)
            driver = self.create_driver(config)

            if config.profile is not None:
                Profile.profile = config.profile

            driver.task_id = self.task_id
            driver.task_path = self.task_path
            driver.beep = task_config.beep
            self.beep = task_config.beep

            final_image_path = f'{self.task_path}/{final_image}'
            
            
            if config.is_tiny_profile:
                load_cookies(driver, config)

            def close_driver(driver):
                print("Closing Browser")                
                if config.is_tiny_profile:
                    save_cookies(driver, config)
                # set tiny profile data
                driver.close()
                print("Closed Browser")                

            result = None
            try:
                result = self.run(driver, data)
                end_task(driver)
                close_driver(driver)
                print(f'View Final Screenshot at {final_image_path}')
                return result
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
                    if not task_config.close_on_crash:
                        driver.prompt("Press Enter To Close Browser")
                    
                close_driver(driver)

                print(f'Task Failed! View Final Screenshot at {final_image_path}')
                return result

        final = run_task(False, 0)

        Profile.profile = None

        return final

    def run(self, driver: BoseDriver, data: any):
        pass

    def is_new_user(self):
        count = LocalStorage.get_item('count', 0)
        return count  <= 5

