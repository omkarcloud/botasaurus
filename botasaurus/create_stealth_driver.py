from javascript_fixes.errors import JavaScriptError
from sys import argv
from .exceptions import CloudflareDetection
from .check_and_download_driver import check_and_download_driver
from typing import Callable, Any, Optional, Union
from .opponent import Opponent
from .anti_detect_driver import AntiDetectDriver
from time import sleep, time
from .chrome_launcher_adapter import ChromeLauncherAdapter
from .create_driver_utils import create_selenium_driver, do_create_driver_with_custom_driver_creator
from selenium.webdriver.chrome.options import Options
import subprocess
from os import name

def kill_process_by_pid(pid):
    if pid is None:
        raise ValueError("A PID must be provided")
    try:
        if name == 'nt':
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # macOS and Linux share the same command for killing a process by PID
            subprocess.run(['kill', str(pid)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # already killed
        pass
    except Exception as e:
        print(f"An error occurred while trying to kill the process with PID {pid}: {e}")


# COPIED FROM chrome-launcher code (https://github.com/GoogleChrome/chrome-launcher/blob/main/src/flags.ts), Mostly same but the extensions, media devices etc are not disabled to avoid detection
DEFAULT_FLAGS = [
    #   safe browsing service, upgrade detector, translate, UMA
    "--disable-background-networking",
    # Don't update the browser 'components' listed at chrome://components/
    "--disable-component-update",
    # Disables client-side phishing detection.
    "--disable-client-side-phishing-detection",
    # Disable syncing to a Google account
    "--disable-sync",
    # Disable reporting to UMA, but allows for collection
    "--metrics-recording-only",
    # Disable installation of default apps on first run
    "--disable-default-apps",
    # Disable the default browser check, do not prompt to set it as such
    "--no-default-browser-check",
    # Skip first run wizards
    "--no-first-run",
    # Disable backgrounding renders for occluded windows
    "--disable-backgrounding-occluded-windows",
    # Disable renderer process backgrounding
    "--disable-renderer-backgrounding",
    # Disable task throttling of timer tasks from background pages.
    "--disable-background-timer-throttling",
    # Disable the default throttling of IPC between renderer & browser processes.
    "--disable-ipc-flooding-protection",
    # Avoid potential instability of using Gnome Keyring or KDE wallet. crbug.com/571003 crbug.com/991424
    "--password-store=basic",
    # Use mock keychain on Mac to prevent blocking permissions dialogs
    "--use-mock-keychain",
    # Disable background tracing (aka slow reports & deep reports) to avoid 'Tracing already started'
    "--force-fieldtrials=*BackgroundTracing/default/",
    # Suppresses hang monitor dialogs in renderer processes. This flag may allow slow unload handlers on a page to prevent the tab from closing.
    "--disable-hang-monitor",
    # Reloading a page that came from a POST normally prompts the user.
    "--disable-prompt-on-repost",
    # Disables Domain Reliability Monitoring, which tracks whether the browser has difficulty contacting Google-owned sites and uploads reports to Google.
    "--disable-domain-reliability",
]


def safe_remove(lst, items):
    """Safely remove an item from a list if it exists"""
    for item in items:
        try:
            lst.remove(item)
        except ValueError:
            pass
    return lst



def clean_options(options):
    options._arguments = safe_remove(
        options._arguments,
        [
            "--disable-site-isolation-trials",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    return options

def launch_chrome(start_url, additional_args):

    unique_flags = list(dict.fromkeys(DEFAULT_FLAGS + additional_args))

    kwargs = {
        "ignoreDefaultFlags": True,
        "chromeFlags": unique_flags,
    }

    if start_url:
        kwargs["startingUrl"] = start_url

    instance = ChromeLauncherAdapter.launch(**kwargs)
    return instance


def get_rayid(driver:AntiDetectDriver):
    ray = driver.text(".ray-id code")
    if ray:
      return ray


def get_iframe(driver:AntiDetectDriver):
      return driver.get_element_or_none_by_selector(
                        '#turnstile-wrapper iframe', None
                    )

def wait_till_cloudflare_leaves(driver:AntiDetectDriver, previous_ray_id, raise_exception):

    WAIT_TIME = 30
    start_time = time()
    while True:
        opponent = driver.get_bot_detected_by()
        if opponent != Opponent.CLOUDFLARE:
            return 
        current_ray_id = get_rayid(driver)
        if current_ray_id:
          
          israychanged = current_ray_id != previous_ray_id
          
          if israychanged:

            WAIT_TIME = 12
            start_time = time()

            while True:
                # if iframe:
                #     print(iframe)
                    
                    iframe = get_iframe(driver)
                    driver.switch_to.frame(iframe)
                    # 
                    
                    checkbox = driver.get_element_or_none_by_selector(
                        '[type="checkbox"]', None
                    )
                    takinglong = driver.get_element_or_none_by_text_contains("is taking longer than expected", None)
                    if takinglong or checkbox:
                        driver.switch_to.default_content()

                        # new captcha given 
                        print("Cloudflare has detected us. Exiting ...")
                        if raise_exception:
                            raise CloudflareDetection()
                        return

                    elapsed_time = time() - start_time
                    if elapsed_time > WAIT_TIME:
                        driver.switch_to.default_content()

                        print("Cloudflare has not given us a captcha. Exiting ...")
                        
                        if raise_exception:
                            raise CloudflareDetection()

                        return
                    
                    driver.switch_to.default_content()
                    
                    opponent = driver.get_bot_detected_by()
                    if opponent != Opponent.CLOUDFLARE:
                        return 

                    sleep(1.79)
                    

        elapsed_time = time() - start_time
        if elapsed_time > WAIT_TIME:
            print("Cloudflare is taking too long to verify Captcha Submission. Exiting ...")
            if raise_exception:
              raise CloudflareDetection()
            
            return

        sleep(0.83)

def bypass_detection(driver: AntiDetectDriver, raise_exception):
    opponent = driver.get_bot_detected_by()
    if opponent == Opponent.CLOUDFLARE:
            iframe = get_iframe(driver)
            while not iframe:
              opponent = driver.get_bot_detected_by()
              if opponent != Opponent.CLOUDFLARE:
                return 
              sleep(1)
              iframe = get_iframe(driver)
            previous_ray_id = get_rayid(driver)
            driver.switch_to.frame(iframe)

            WAIT_TIME = 8
            start_time = time()

            while True:
                checkbox = driver.get_element_or_none_by_selector(
                    '[type="checkbox"]', None
                )
                if checkbox:
                    checkbox.click()
                    driver.switch_to.default_content()
                    wait_till_cloudflare_leaves(driver, previous_ray_id, raise_exception)
                    return

                elapsed_time = time() - start_time
                if elapsed_time > WAIT_TIME:
                    driver.switch_to.default_content()

                    print("Cloudflare has not given us a captcha. Exiting ...")
                    
                    if raise_exception:
                        raise CloudflareDetection()

                    return
                sleep(1.79)


def add_server_args(options):
    if '--disable-dev-shm-usage' not in options._arguments:
        options.add_argument('--disable-dev-shm-usage')
    if '--no-sandbox' not in options._arguments:
        options.add_argument('--no-sandbox')
    if '--headless=new' not in options._arguments:
        options.add_argument('--headless=new')

def is_server_mode():
    # Check if '--server' is in the list of command-line arguments
    return '--server' in argv

def launch_server_safe_chrome(options, start_url):
    try:
        return launch_chrome(start_url, options._arguments)
    except JavaScriptError as e:
        if "ECONNREFUSED" in e.js and not is_server_mode():
            add_server_args(options)
            print("Chrome failed to launch. Retrying with additional server options. To add server options by default, include '--server' in your launch command.")
            return launch_chrome(start_url, options._arguments)
        raise

def do_create_stealth_driver(data, options, desired_capabilities, start_url, wait,  raise_exception,add_arguments):
    options = clean_options(options)
    if add_arguments:
      add_arguments(data, options)
    
    chrome = launch_server_safe_chrome(options, start_url)
    debug_port = chrome.port

    should_wait = start_url and wait
    if should_wait:
            print(f"Waiting {wait} seconds before connecting to Chrome...")
            sleep(wait)

    remote_driver_options = Options()

    remote_driver_options.add_experimental_option(
        "debuggerAddress", f"127.0.0.1:{debug_port}"
    )
    remote_driver = create_selenium_driver(remote_driver_options, desired_capabilities)
    pid = chrome.pid

    remote_driver.kill_chrome_by_pid = lambda: kill_process_by_pid(pid)

    if not should_wait:
            sleep(1) # Still do some wait to prevent exceptions

    # input('after create')
    try:
        if start_url:
            bypass_detection(remote_driver, raise_exception)
    except CloudflareDetection as e:
        
        try:
            remote_driver.close()
            remote_driver.quit()
        except:
            pass

        raise e


    return remote_driver


def create_stealth_driver(start_url:Optional[Union[Callable[[Any], str], str]]="NONE", wait=8, 
                          
                          raise_exception=False, 
                          add_arguments: Optional[Callable[[Any, Options], None]] = None, ):
    
    def run(data, options, desired_capabilities):
        evaluated_start_url = start_url(data) if callable(start_url) else start_url
        if evaluated_start_url == "NONE":
            message = """To best stealthiness against Cloudflare and other bot detectors, it is recommended to provide a "start_url" to create_stealth_driver. 
    However, if you wish not to start Chrome with a URL, you can pass 'None' as the argument. For example: 

    create_driver = create_stealth_driver(start_url=None)
    """
            raise ValueError(message)
        return do_create_stealth_driver(
        data, options, desired_capabilities, evaluated_start_url, wait,  raise_exception, add_arguments,
    )

    return run


def create_stealth_driver_instance(start_url:Optional[Union[Callable[[Any], str], str]]="NONE", wait=8, 
                                   raise_exception=False, 
                                   add_arguments: Optional[Callable[[Any, Options], None]] = None):
    check_and_download_driver()
    def create_driver(options, desired_capabilities):
        return create_stealth_driver(start_url=start_url, wait=wait,raise_exception=raise_exception, add_arguments=add_arguments)({}, options, desired_capabilities)
    return do_create_driver_with_custom_driver_creator(None, None, None, None, None, False, False, None, False, False, True,  create_driver)

if __name__ == "__main__":
    chrome = launch_chrome("https://www.000webhost.com/cpanel-login", [])
    create_stealth_driver()
