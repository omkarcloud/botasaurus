import requests
from requests.exceptions import ReadTimeout
import traceback
from .botasaurus_storage import get_botasaurus_storage


def _create_proxy_dict(proxy_url: str) -> dict:
    """Converts a proxy URL string into a dictionary for the requests library."""
    return {"http": proxy_url, "https": proxy_url}


def _find_ip(attempts=5, proxy=None, is_retry = False) -> str:
    """Finds the public IP address of the current connection."""
    # Server may be down so check this
    if is_retry:
        url = "https://api.ipify.org"
    else:
        url = "https://checkip.amazonaws.com/"
    
    proxies = _create_proxy_dict(proxy) if proxy else None

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        return response.text.strip()

    except ReadTimeout:
        if attempts > 1:
            print("ReadTimeout occurred. Retrying...")
            return _find_ip(attempts - 1, proxy, True)
        else:
            print("Max attempts reached. Failed to get IP address.")
            return None

    except Exception:
        traceback.print_exc()
        return None


def _load_cache() -> dict:
    """Loads the IP details cache from a file."""
    return get_botasaurus_storage().get_item("ip_details_cache", {})


def _save_cache(cache: dict):
    """Saves the IP details cache to a file."""
    return get_botasaurus_storage().set_item("ip_details_cache", cache)


def reorganize_dict_by_importance(input_dict):
    priority_keys = [
        "ip",
        "country",
        "region",
        "city",
        "postal",
        "coordinates",
        "latitude",
        "longitude",
        "timezone",
        "org",
    ]

    output_dict = {}

    for key in priority_keys:
        output_dict[key] = input_dict.get(key, None)

    return output_dict


def get_ip_info(
    proxy=None,
    max_retries=5,
):
    """Finds details about the current public IP address."""
    cache = _load_cache()

    current_ip = _find_ip(proxy=proxy)
    if current_ip is None:
        return None

    # Check if details are already cached
    if current_ip in cache:
        return cache[current_ip]

    url = "https://ipinfo.io"
    proxies = _create_proxy_dict(proxy) if proxy else None

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        data = response.json()

        try:
            loc = data["loc"]
            data["coordinates"] = loc
            data["latitude"], data["longitude"] = loc.split(",")
        except:
            pass
        data = reorganize_dict_by_importance(data)
        # Cache the data
        cache[current_ip] = data
        _save_cache(cache)
        return data

    except requests.exceptions.ReadTimeout:
        if max_retries > 0:
            return get_ip_info(max_retries - 1, proxy)
        else:
            return None
    except Exception as e:
        return None

class IPUtils:
    @staticmethod
    def get_ip(proxy=None):
        """
        Finds the IP address of the current connection.
        
        Example: 47.31.226.180
        """
        ip = _find_ip(proxy=proxy)
        while ip is None:
            print("Failed to get IP. Retrying...")
            ip = _find_ip(proxy=proxy)
        return ip

    @staticmethod
    def get_ip_info(proxy=None):
        """
        Finds details about the current IP address.
        
        Example:
        {
            "ip": "47.31.226.180",
            "country": "IN",
            "region": "Delhi",
            "city": "Delhi",
            "postal": "110001",
            "coordinates": "28.6519,77.2315",
            "latitude": "28.6519",
            "longitude": "77.2315",
            "timezone": "Asia/Kolkata",
            "org": "AS55836 Reliance Jio Infocomm Limited"
        }
        """
        return get_ip_info(proxy)