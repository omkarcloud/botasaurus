import requests
from requests.exceptions import ReadTimeout
import traceback
from .botasaurus_storage import BotasaurusStorage

def create_proxy_dict(proxy_url: str) -> dict:
    """Converts a proxy URL string into a dictionary for the requests library."""
    return {"http": proxy_url, "https": proxy_url}

def find_ip(attempts=5, proxy=None) -> str:
    """Finds the public IP address of the current connection."""
    url = 'https://checkip.amazonaws.com/'
    proxies = create_proxy_dict(proxy) if proxy else None

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        return response.text.strip()

    except ReadTimeout:
        if attempts > 1:
            print("ReadTimeout occurred. Retrying...")
            return find_ip(attempts - 1, proxy)
        else:
            print("Max attempts reached. Failed to get IP address.")
            return None

    except Exception as e:
        traceback.print_exc()
        return None

def load_cache() -> dict:
    """Loads the IP details cache from a file."""
    return BotasaurusStorage.get_item("ip_details_cache", {})

def save_cache(cache: dict):
    """Saves the IP details cache to a file."""
    return BotasaurusStorage.set_item("ip_details_cache", cache)

def find_ip_details(max_retries=5, proxy=None):
    """Finds details about the current public IP address."""
    cache = load_cache()

    current_ip = find_ip(proxy=proxy)
    if current_ip is None:
        return None

    # Check if details are already cached
    if current_ip in cache:
        return cache[current_ip]

    url = 'https://ipinfo.io'
    proxies = create_proxy_dict(proxy) if proxy else None

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        data = response.json()

        if "readme" in data:
            del data["readme"]

        # Cache the data
        cache[current_ip] = data
        save_cache(cache)
        return data

    except requests.exceptions.ReadTimeout:
        if max_retries > 0:
            return find_ip_details(max_retries - 1, proxy)
        else:
            return None
    except Exception as e:
        return None




def get_valid_ip():
    ip = find_ip()
    while ip is None:
        print("Failed to get IP. Retrying...")
        ip = find_ip()
    return ip
