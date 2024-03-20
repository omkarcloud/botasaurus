
from cloudscraper import CloudScraper
from bs4 import BeautifulSoup
from requests.models import Response
from .got_adapter import GotAdapter
# Create a subclass of CloudScraper
class AntiDetectRequests(CloudScraper):
    
    def __init__(self, *args, use_stealth=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_stealth = use_stealth

    def request(self, method, url, *args, **kwargs):
        if self.use_stealth:
            # Use static methods of GotAdapter for making the request
            got_method = getattr(GotAdapter, method.lower(), None)
            
            
            if 'proxies' not in kwargs and hasattr(self, 'proxies') and getattr(self, 'proxies', None):
              kwargs.update({'proxies': getattr(self, 'proxies', None)})
            
            if got_method:
                return got_method(url, *args, **kwargs)
            else:
                raise NotImplementedError(f"Method {method} is not implemented in GotAdapter.")
        else:
            # Pass all arguments to the parent CloudScraper class
            return super().request(method, url, *args, **kwargs)

    def get(self, url, 
            referer='https://www.google.com/', 
            params = None,
            data = None,
            headers = None,
            cookies = None,
            files = None,
            auth = None,
            timeout = None,
            allow_redirects = None,
            proxies = None,
            hooks = None,
            stream = None,
            verify = None,
            cert = None,
            json = None,
            **kwargs) -> Response:
    

        # Only update kwargs with non-None named arguments
        named_args = {
            'params': params, 'data': data, 'headers': headers, 'cookies': cookies,
            'files': files, 'auth': auth, 'timeout': timeout, 
            'allow_redirects': allow_redirects, 'proxies': proxies, 'hooks': hooks, 
            'stream': stream, 'verify': verify, 'cert': cert, 'json': json
        }
        updated = {k: v for k, v in named_args.items() if v is not None}
        kwargs.update(updated)
        
        headers = kwargs.get('headers', {})

        # Set the referrer only if it's not None and 'Referer' is not already set in headers
        if referer is not None and ('Referer' not in headers or 'referer' not in headers):
            headers['Referer'] = referer
            kwargs['headers'] = headers

        kwargs.setdefault("allow_redirects", True)
            # Use static methods of GotAdapter for making the request
        return self.request("GET", url, **kwargs)


    # Method to get bs4 object by passing a URL
    def bs4(self, url, 
             referer='https://www.google.com/', 
            params = None,
            data = None,
            headers = None,
            cookies = None,
            files = None,
            auth = None,
            timeout = None,
            allow_redirects = None,
            proxies = None,
            hooks = None,
            stream = None,
            verify = None,
            cert = None,
            json = None,
             **kwargs) -> BeautifulSoup:
        # Only update kwargs with non-None named arguments
        named_args = {
            'referer': referer,
            'params': params,
              'data': data, 'headers': headers, 'cookies': cookies,
            'files': files, 'auth': auth, 'timeout': timeout, 
            'allow_redirects': allow_redirects, 'proxies': proxies, 'hooks': hooks, 
            'stream': stream, 'verify': verify, 'cert': cert, 'json': json
        }
        updated = {k: v for k, v in named_args.items() if v is not None}
        kwargs.update(updated)
        
        
        response = self.get(url,  **kwargs)
        
        # Check if the request was successful
        if response.status_code < 299:
            # Create a BeautifulSoup object from the response text
            return BeautifulSoup(response.text, 'html.parser')
        else:
            # Raise an HTTPError for bad requests
            response.raise_for_status()

    # Method to get bs4 object by passing a URL
    def response_to_bs4(self, response):
            return BeautifulSoup(response.text, 'html.parser')

    # 

    # TODO REMOVE
    # def google_get(self, url, **kwargs):
    #         kwargs['headers'] = {**kwargs.get('headers', {}), 'Referer':"https://www.google.com/"}
    #         return self.get(url, **kwargs)

