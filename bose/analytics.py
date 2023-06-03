from .local_storage import LocalStorage
import requests

class Analytics:
    def send_tracking_data():
        try:
            cookies = {}
            headers = {}
            json_data = {
                'type': 'bose_usage',
                'data': {
                    "count": LocalStorage.get_item('count', 0)
                },
            }

            response = requests.post('https://www.omkar.cloud/backend/actions/', 
                                    #  cookies=cookies, headers=headers, 
                                     json=json_data)
        except Exception as e:
            # raise e
            pass