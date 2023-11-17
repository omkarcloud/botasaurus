from .create_driver_utils import do_download_driver
from .utils import    relative_path
from .get_chrome_version import get_driver_path
import os

# Global variable to track if the check has been done
check_done = False

def has_driver():
            driver_path =  relative_path(get_driver_path(), 0)
            return os.path.isfile(driver_path)

def check_and_download_driver():
    global check_done

    # Check if the check has already been done
    if check_done:
        return

    check_done = True
    if not has_driver():
         do_download_driver()

