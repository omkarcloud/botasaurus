from .anti_detect_driver import AntiDetectDriver
from selenium.common.exceptions import WebDriverException

from .anti_detect_requests import AntiDetectRequests
from .create_driver_utils import delete_corrupted_files, do_create_driver
from .utils import NETWORK_ERRORS, retry_if_is_error
from .check_and_download_driver import check_and_download_driver

def create_driver(tiny_profile=False, profile=None, window_size=None, user_agent=None, proxy=None, is_eager=False, headless=False, lang=None, block_resources=False, block_images=False, beep=False) -> AntiDetectDriver:
    check_and_download_driver()
    return retry_if_is_error(
        lambda: do_create_driver(tiny_profile, profile, window_size, user_agent, proxy, is_eager, headless, lang, block_resources, block_images, beep),
        NETWORK_ERRORS + [(WebDriverException, lambda: delete_corrupted_files(profile) if profile else None)],
        5
    )

def create_requests(proxy=None,  user_agent=None, use_stealth=False,):

    # Use windows, chrome (most common) and mixing other platforms and browsers causes bot detection
    
    if use_stealth:
      if user_agent:
        raise ValueError("user_agent can not be used in stealth")
    
    if user_agent:
        reqs = AntiDetectRequests(
            use_stealth=use_stealth,
            browser={
                'custom': user_agent,
            }
        )
    else:
        reqs = AntiDetectRequests(
            use_stealth=use_stealth,
            browser={
                'platform': 'windows',
                'browser': 'chrome',
                'mobile': False
            }
        )
    if proxy is not None:
        reqs.proxy =  proxy
        reqs.proxies = {
            'http': proxy,
            'https': proxy,
        }
    else:
        reqs.proxy = None
        
    return reqs
