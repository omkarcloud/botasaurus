import requests
from requests.exceptions import ReadTimeout
import traceback
def find_ip_details(max_retries=5):
    url = 'https://www.omkar.cloud/backend/ipinfo/'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if "readme" in data:
           del data["readme"]
        return data
    except requests.exceptions.ReadTimeout:
        if max_retries > 0:
            print('ReadTimeout occurred. Retrying...')
            return find_ip_details(max_retries - 1)
        else:
            print('Max retries exceeded. Unable to fetch IP details.')
            return None
    except Exception as e:
        traceback.print_exc()
        return None

def find_ip(attempts=5):
    url = 'https://checkip.amazonaws.com/'
    try:
        response = requests.get(url, timeout=10)
        return response.text.strip()

    except ReadTimeout:
        if attempts > 1:
            print("ReadTimeout occurred. Retrying...")
            return find_ip(attempts - 1)
        else:
            print("Max attempts reached. Failed to get IP address.")
            return None

    except Exception as e:
        traceback.print_exc()
        return None


def get_valid_ip():
    ip = find_ip()
    while ip is None:
        print("Failed to get IP. Retrying...")
        ip = find_ip()
    return ip
