from selenium.common.exceptions import WebDriverException
from bose.user_agent import UserAgentInstance, UserAgent
from bose.window_size import WindowSize, WindowSizeInstance
from bose.utils import relative_path, silentremove
from selenium.webdriver.chrome.options import Options as GoogleChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from undetected_chromedriver.v2 import ChromeOptions
from bose.drivers.boss_driver import BossDriver

from bose.drivers.boss_undetected_driver import BossUndetectedDriver
import shutil

class RetryException(Exception):
    pass


class BrowserConfig:
    def __init__(self, user_agent=None, window_size=WindowSize.window_size_1920_1080, profile=None, is_eager=False, use_undetected_driver=False):
        self.user_agent = user_agent
        self.window_size = window_size
        self.profile = profile
        self.is_eager = is_eager
        self.use_undetected_driver = use_undetected_driver


def delete_cache(driver):
    print('Deleting Cache')
    driver.command_executor._commands['SEND_COMMAND'] = (
        'POST', '/session/$sessionId/chromium/send_command'
    )
    driver.execute('SEND_COMMAND', dict(
        cmd='Network.clearBrowserCache', params={}))


def add_useragent(options, user_agent):
    options.add_argument(f'--user-agent={user_agent}')

def create_profile_path(user_id):
    PROFILES_PATH = 'profiles'
    PATH = f'{PROFILES_PATH}/{user_id}'
    path = relative_path(PATH, 0)
    return path


def delete_corrupted_files(user_id):
    is_success = silentremove(
        f'{create_profile_path(user_id)}/SingletonCookie')
    silentremove(f'{create_profile_path(user_id)}/SingletonSocket')
    silentremove(f'{create_profile_path(user_id)}/SingletonLock')

    if is_success:
        print('Fixed Profile by deleting Corrupted Files')
    else:
        print('No Corrupted Profiles Found')


def delete_profile_path(user_id):
    path = create_profile_path(user_id)
    shutil.rmtree(path, ignore_errors=True)


def add_essential_options(options, profile, window_size, user_agent):
    options.add_argument("--start-maximized")
    
    if window_size == None:
        if profile == None:
            window_size = WindowSizeInstance.get_random()
        else:
            window_size = WindowSizeInstance.get_hashed(profile)
    else: 
        if window_size == WindowSize.RANDOM:
            window_size = WindowSizeInstance.get_random(profile)
        elif window_size == WindowSize.HASHED:
            window_size = WindowSizeInstance.get_hashed(profile)
        else: 
            window_size = window_size
    
    window_size = WindowSize.window_size_to_string(window_size)
    options.add_argument(f"--window-size={window_size}")

    if user_agent == None:
        if profile == None:
            user_agent = UserAgentInstance.get_random()
        else:
            user_agent = UserAgentInstance.get_hashed(profile)
    else: 
        if user_agent == UserAgent.RANDOM:
            user_agent = UserAgentInstance.get_random(profile)
        elif user_agent == UserAgent.HASHED:
            user_agent = UserAgentInstance.get_hashed(profile)
        else: 
            user_agent = user_agent

    
    add_useragent(options, user_agent)

    has_user = profile is not None
    if has_user:
        path = create_profile_path(profile)
        user_data_path = f"--user-data-dir={path}"
        options.add_argument(user_data_path)

    return {"window_size":window_size, "user_agent":user_agent, "profile": profile}

def get_eager_startegy():

    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
    caps["pageLoadStrategy"] = "none"   # Do not wait for full page load
    return caps



def hide_automation_flags(options):
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-blink-features")

    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # New Options
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")


def is_docker():
    path = '/proc/self/cgroup'

    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
        or os.environ.get('KUBERNETES_SERVICE_HOST') is not None
    )

def get_driver_path():
    executable_name = "chromedriver.exe" if is_windows() else "chromedriver"
    dest_path = f"build/{executable_name}"
    return dest_path

def create_driver(config: BrowserConfig):
    def run():

        is_undetected = config.use_undetected_driver
        options = ChromeOptions() if is_undetected else GoogleChromeOptions()

        if is_docker():
            print("Running in Docker, So adding sandbox arguments")
            options.arguments.extend(
                ["--no-sandbox", "--disable-setuid-sandbox"])

        driver_attributes = add_essential_options(options, config.profile, config.window_size, config.user_agent)

        if driver_attributes["profile"] is not None:
            driver_string = "Creating Driver with profile '{}', window_size={}, and user_agent={}".format(driver_attributes["profile"], driver_attributes["window_size"], driver_attributes["user_agent"])
        else:
            driver_string = "Creating Driver with window_size={} and user_agent={}".format(driver_attributes["window_size"], driver_attributes["user_agent"])
      
        if config.is_eager:
            desired_capabilities = get_eager_startegy()
        else:
            desired_capabilities = None
        
        print(driver_string)

        if is_undetected:
            driver = BossUndetectedDriver(desired_capabilities=desired_capabilities,
                              options=options
                            )
        else:
            # options.add_experimental_option("prefs",  {"profile.managed_default_content_settings.images": 2})
            hide_automation_flags(options)
            
            # CAPTCHA
            options.arguments.extend(
                ["--disable-web-security", "--disable-site-isolation-trials", "--disable-application-cache"])

            path = relative_path(get_driver_path(), 0)

            print(f'driver path: {path}' )

            driver = BossDriver(
                desired_capabilities=desired_capabilities,
                chrome_options=options,
                executable_path=path,
            )

        if driver_attributes["profile"] is None:
            del driver_attributes["profile"]

        driver._init_data = driver_attributes
        return driver
    driver = retry_if_is_error(
                run, NETWORK_ERRORS + [(WebDriverException, lambda: delete_corrupted_files(config.profile) if config.profile else None )], 5)
    print("Launched Browser")

    return driver
