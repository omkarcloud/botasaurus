import subprocess
import platform

def close_all_chrome_browsers():
    os_name = platform.system()
    try:
        if os_name == 'Windows':
            # taskkill /F /IM chrome.exe
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os_name == 'Darwin':  # macOS
            subprocess.run(['pkill', 'Google Chrome'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os_name == 'Linux':
            subprocess.run(['pkill', 'chrome'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # No else case is needed since no output is desired
    except subprocess.CalledProcessError:
        # Silently ignore the error when no Chrome processes are found
        pass
    except Exception:
        # Silently ignore the error
        pass


if __name__ == "__main__":
    close_all_chrome_browsers()
