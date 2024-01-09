from .check_and_download_driver import check_and_download_driver
from typing import Callable, Any, Optional
from .opponent import Opponent
from .anti_detect_driver import AntiDetectDriver
from time import sleep, time
from .chrome_launcher_adapter import ChromeLauncherAdapter
from .create_driver_utils import create_selenium_driver, do_create_driver_with_custom_driver_creator
from selenium.webdriver.chrome.options import Options


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


def wait_till_cloudflare_leaves(driver):
    WAIT_TIME = 6

    while True:
        opponent = driver.get_bot_detected_by()
        if opponent != Opponent.CLOUDFLARE:
            return 

        start_time = time()
        elapsed_time = time() - start_time
        if elapsed_time > WAIT_TIME:
            return

        sleep(0.83)

def bypass_detection(driver: AntiDetectDriver):
    opponent = driver.get_bot_detected_by()
    if opponent == Opponent.CLOUDFLARE:
        iframe = driver.get_element_or_none_by_selector("iframe")
        if iframe:
            driver.switch_to.frame(iframe)
            start_time = time()

            WAIT_TIME = 8

            while True:
                checkbox = driver.get_element_or_none_by_selector(
                    '[type="checkbox"]', None
                )
                if checkbox:
                    # sleep(1.7)
                    checkbox.click()
                    driver.switch_to.default_content()
                    wait_till_cloudflare_leaves(driver)

                    return

                elapsed_time = time() - start_time
                if elapsed_time > WAIT_TIME:
                    print("Failed to solve Cloudflare Captcha")
                    driver.switch_to.default_content()
                    return
                sleep(1.79)

            # get bot detected
            # if is cloudflare
            # switch to frame
            # while True
    # if checkbox (2 second wait)
    # then click
    # switch to default
    # return
    # find checkbox

    # then while True
    #  If get to
    #

    #


def do_create_stealth_driver(data, options, desired_capabilities, start_url, wait, add_arguments):
    options = clean_options(options)
    if add_arguments:
      add_arguments(data, options)
    
    chrome = launch_chrome(start_url, options._arguments)
    debug_port = chrome.port


    if start_url:
        if wait:
            print(f"Waiting {wait} seconds before connecting to Chrome...")
            sleep(wait)

    remote_driver_options = Options()

    remote_driver_options.add_experimental_option(
        "debuggerAddress", f"127.0.0.1:{debug_port}"
    )

    remote_driver = create_selenium_driver(remote_driver_options, desired_capabilities)

    # input('after create')
    if start_url:
        bypass_detection(remote_driver)
    return remote_driver


def create_stealth_driver(start_url="NONE", wait=8, add_arguments: Optional[Callable[[Options], None]] = None):
    if start_url == "NONE":
        message = """To best stealthiness against Cloudflare and other bot detectors, it is recommended to provide a "start_url" to create_stealth_driver. 
However, if you wish not to start Chrome with a URL, you can pass 'None' as the argument. For example: 

create_driver = create_stealth_driver(start_url=None)
"""
        raise ValueError(message)

    return lambda data, options, desired_capabilities: do_create_stealth_driver(
        data, options, desired_capabilities, start_url, wait, add_arguments
    )


def create_stealth_driver_instance(start_url="NONE", wait=8, add_arguments: Optional[Callable[[Options], None]] = None):
    check_and_download_driver()
    def create_driver(options, desired_capabilities):
        return create_stealth_driver(start_url=start_url, wait=wait, add_arguments=add_arguments)({}, options, desired_capabilities)
    return do_create_driver_with_custom_driver_creator(None, None, None, None, None, False, False, None, False, False, True,  create_driver)

if __name__ == "__main__":
    chrome = launch_chrome("https://www.000webhost.com/cpanel-login", [])
    create_stealth_driver()
