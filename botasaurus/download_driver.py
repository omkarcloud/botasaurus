import os
import shutil

import chromedriver_autoinstaller_fix
from chromedriver_autoinstaller_fix import get_chrome_version
from chromedriver_autoinstaller_fix.utils import get_major_version


def is_windows():
    return os.name == 'nt'

def download_driver_in_path():
    path = chromedriver_autoinstaller_fix.install(path='build/')  
    # print(path)

def recreate_build_dir():
    # Get the path of the current working directory
    current_dir = os.getcwd()

    # Construct the path of the build directory
    build_dir = os.path.join(current_dir, "build")

    # Delete the build directory
    shutil.rmtree(build_dir, ignore_errors=True)

    # Create the build directory again
    os.makedirs(build_dir)


def get_filename(major_version):
    return f"chromedriver-{major_version}.exe" if is_windows() else f"chromedriver-{major_version}"

def move_driver():
    major_version = get_major_version(get_chrome_version())

    executable_name = get_filename(major_version)
    executable_name_src = "chromedriver.exe" if is_windows() else "chromedriver"

    def move_chromedriver():
        # Define the source and destination paths
        src_path = f"build/{major_version}/{executable_name_src}"
        dest_path = f"build/{executable_name}"

        # Use the shutil.move() function to move the file
        shutil.move(src_path, dest_path)
    move_chromedriver()
    shutil.rmtree(f"build/{major_version}/")


def download_driver():
    
    recreate_build_dir()
    print(f'[INFO] Downloading Chrome Driver. This is a one-time process. Download in progress...')

    download_driver_in_path()
    move_driver()

if __name__ == '__main__':
    download_driver()