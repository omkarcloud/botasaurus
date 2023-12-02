from time import sleep
import os

from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from shutil import rmtree
from botasaurus.get_chrome_version import get_driver_path

from .driver_about import AboutBrowser
from .anti_detect_driver import AntiDetectDriver
from .user_agent import UserAgent, UserAgentInstance
from .utils import get_current_profile_path, read_json, relative_path, silentremove, write_json
from .window_size import WindowSize, WindowSizeInstance


def get_eager_strategy():
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"   # Do not wait for full page load
    return caps


def delete_cache(driver):
    print('Deleting Cache')
    driver.command_executor._commands['SEND_COMMAND'] = (
        'POST', '/session/$sessionId/chromium/send_command'
    )
    driver.execute('SEND_COMMAND', dict(
        cmd='Network.clearBrowserCache', params={}))

def add_useragent(options, user_agent):
    if user_agent:
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
    rmtree(path, ignore_errors=True)



def add_essential_options(options, profile, window_size, user_agent):
    options.add_argument("--start-maximized")
    if window_size != WindowSize.REAL:
        if window_size == None:
            if profile == None:
                window_size = WindowSizeInstance.get_random()
            else:
                window_size = WindowSizeInstance.get_hashed(profile)
        else:
            if window_size == WindowSize.RANDOM:
                window_size = WindowSizeInstance.get_random()
            elif window_size == WindowSize.HASHED:
                window_size = WindowSizeInstance.get_hashed(profile)
            else:
                window_size = window_size

        window_size = WindowSize.window_size_to_string(window_size)
        options.add_argument(f"--window-size={window_size}")

    if profile is not None:
        profile = str(profile)

    if user_agent != UserAgent.REAL:
        if user_agent == None:
            if profile == None:
                user_agent = UserAgentInstance.get_random()
            else:
                user_agent = UserAgentInstance.get_hashed(profile)
        else:
            if user_agent == UserAgent.RANDOM:
                user_agent = UserAgentInstance.get_random()
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

    return {"window_size": window_size, "user_agent": user_agent, "profile": profile}

def hide_automation_bar(options):
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-blink-features")

    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)



def is_gitpod_environment():
    return 'GITPOD_WORKSPACE_ID' in os.environ

def is_docker():
    path = '/proc/self/cgroup'

    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
        or os.environ.get('KUBERNETES_SERVICE_HOST') is not None
    )


def get_current_profile_path(profile): 
    profiles_path = f'profiles/{profile}/'
    # profiles_path =  relative_path(path, 0)
    return profiles_path

# Possible states for driver download
NOT_DOWNLOADED = 0
DOWNLOADING = 1
DOWNLOADED = 2

driver_download_state = NOT_DOWNLOADED


def do_download_driver():
    global driver_download_state
    
    # Check the state
    while True:
        if driver_download_state == NOT_DOWNLOADED:
            # Change the state to DOWNLOADING
            driver_download_state = DOWNLOADING
            break
        elif driver_download_state == DOWNLOADING:
            # If another thread is already downloading, wait
            sleep(0.1)  # Sleep to prevent a busy-wait loop that hogs the CPU
        else:
            # If the driver is already downloaded, just return
            return    
    try:
        from .download_driver import download_driver
        download_driver()
    finally:
        # Change the state to DOWNLOADED after completion or if an exception occurs
        driver_download_state = DOWNLOADED

# def do_download_driver():
    
#     from .download_driver import download_driver
#     download_driver()

def save_cookies(driver, profile):
            current_profile_data = get_current_profile_path(profile) + 'profile.json'
            current_profile_data_path =  relative_path(current_profile_data, 0)

            driver.execute_cdp_cmd('Network.enable', {})
            cookies = (driver.execute_cdp_cmd('Network.getAllCookies', {}))
            driver.execute_cdp_cmd('Network.disable', {})

            if type(cookies) is not list:
                cookies = cookies.get('cookies')
            write_json(cookies, current_profile_data_path)


def load_cookies(driver: AntiDetectDriver, profile):
    current_profile = get_current_profile_path(profile)
    current_profile_path = relative_path(current_profile, 0)

    if not os.path.exists(current_profile_path):
        os.makedirs(current_profile_path)

    current_profile_data = get_current_profile_path(profile) + 'profile.json'
    current_profile_data_path = relative_path(current_profile_data, 0)

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
        cookie['domain'] = cookie['domain'].replace(
            'apple.com', 'microsoft.com')
        # Set the actual cookie
        driver.execute_cdp_cmd('Network.setCookie', cookie)

    driver.execute_cdp_cmd('Network.disable', {})



def create_selenium_driver(proxy, options, desired_capabilities, path, attempt_download=True):
    
    try:
        if proxy is not None:
            from .drivers import AntiDetectDriverSeleniumWire

            selwireOptions = {'proxy': {'http': proxy, 'https': proxy}}

            driver = AntiDetectDriverSeleniumWire(
                desired_capabilities=desired_capabilities,
                seleniumwire_options=selwireOptions,
                chrome_options=options,
                executable_path=path,
            )  
        else:
            driver = AntiDetectDriver(
                desired_capabilities=desired_capabilities,
                chrome_options=options,
                executable_path=path,
            )
            
        return driver

    except SessionNotCreatedException as e:
        if "This version of ChromeDriver only supports Chrome version" in str(e) and attempt_download:
            # Handle the specific case where ChromeDriver version is not compatible
            do_download_driver()
            # Retry creating the Selenium driver once more
            return create_selenium_driver(proxy, options, desired_capabilities, path, attempt_download=False)
        else:
            # If the exception message is different, or we already attempted to download, re-raise the exception
            raise


def add_about(tiny_profile, proxy, lang, beep, driver_attributes, driver):
    about = AboutBrowser(window_size=driver_attributes.get('window_size'), user_agent=driver_attributes.get('user_agent'), profile=driver_attributes.get('profile'),proxy=proxy, lang=lang, beep=beep, is_new=True)
    driver.about = about
    if tiny_profile:
        load_cookies(driver, about.profile)

def do_create_driver(tiny_profile, profile, window_size, user_agent, proxy, is_eager, headless, lang, block_images, beep):

        if tiny_profile and profile is None:
            raise Exception('Profile must be given when using tiny profile')

        options = Options()
        is_gitpod = is_gitpod_environment()

        if is_gitpod:
            # todo: Maybe need to add check to see running in ec2/gcp then I need to also add this or we can make this an error based option add on
            options.add_argument('--disable-dev-shm-usage')

        if headless or is_gitpod:
            options.add_argument('--headless=new')

        if is_docker():
            options.add_argument('--disable-setuid-sandbox')

        if lang is not None:
            options.add_argument(f'--lang={lang}')

        if block_images:
            options.add_experimental_option(
                "prefs", {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.managed_default_content_settings.stylesheet": 2,
                    "profile.managed_default_content_settings.fonts": 2,
                }
            )

        driver_attributes = add_essential_options(
            options, None if tiny_profile else profile, window_size, user_agent)
        
        hide_automation_bar(options)

        # Necessary Options
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        # options.add_argument("--disable-extensions")

        # Captch Options
        if proxy:
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-site-isolation-trials")
            options.add_argument("--disable-application-cache")

        desired_capabilities = get_eager_strategy() if is_eager  else None

        path = relative_path(get_driver_path(), 0)

        driver = create_selenium_driver(proxy, options, desired_capabilities, path)
        driver_attributes['profile'] = profile
        # print(driver_attributes)
        add_about(tiny_profile, proxy, lang, beep, driver_attributes, driver)
        return driver



