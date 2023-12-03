from .anti_detect_driver import AntiDetectDriver
from selenium.common.exceptions import WebDriverException

from .anti_detect_requests import AntiDetectRequests
from .create_driver_utils import delete_corrupted_files, do_create_driver
from .utils import NETWORK_ERRORS, retry_if_is_error
from .check_and_download_driver import check_and_download_driver

def create_driver(tiny_profile=False, profile=None, window_size=None, user_agent=None, proxy=None, is_eager=False, headless=False, lang=None, block_images=False, beep=False) -> AntiDetectDriver:
    check_and_download_driver()
    return retry_if_is_error(
        lambda: do_create_driver(tiny_profile, profile, window_size, user_agent, proxy, is_eager, headless, lang, block_images, beep),
        NETWORK_ERRORS + [(WebDriverException, lambda: delete_corrupted_files(profile) if profile else None)],
        5
    )

def create_requests(proxy):
    # Use windows, chrome (most common) and mixing other platforms and browsers causes bot detection
    reqs = AntiDetectRequests.create_scraper(
        browser={
            'platform': 'windows',
            'browser': 'chrome',
            'mobile': False
        }
    )
                
    if proxy is not None:
        reqs.proxies = {
            'http': proxy,
            'https': proxy,
        }

    return reqs
