import requests
from requests.exceptions import ReadTimeout
import traceback

def find_ip_details():
    url = 'https://www.omkar.cloud/backend/ipinfo/'
    try:
        response = requests.get(url, timeout=10)
        data =  (response.json())

        if "readme" in data:
           del data["readme"]
        return data
    except ReadTimeout:
        print('Refetching IP')
        return find_ip_details()
    except Exception:
        traceback.print_exc()
        return None
    

def find_ip():
    url = 'https://checkip.amazonaws.com/'
    try:
        response = requests.get(url, timeout=10)
        return (response.text).strip()

        # requests.exceptions.ReadTimeout
    except ReadTimeout:
        return None
    except Exception:
        traceback.print_exc()
        return None


def get_valid_ip():
    ip = find_ip()
    while ip is None:
        print("Failed to get IP. Retrying...")
        ip = find_ip()
    return ip
