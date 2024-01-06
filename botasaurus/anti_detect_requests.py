from cloudscraper import CloudScraper
from bs4 import BeautifulSoup

# Create a subclass of CloudScraper
class AntiDetectRequests(CloudScraper):
    
    def __init__(self, *args, use_stealth=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_stealth = use_stealth
        if self.use_stealth:
            # Dynamically import GotAdapter
            global GotAdapter
            from got_adapter import GotAdapter

    def request(self, method, url, *args, **kwargs):
        if self.use_stealth:
            # Use static methods of GotAdapter for making the request
            got_method = getattr(GotAdapter, method.lower(), None)
            if got_method:
                return got_method(url, *args, **kwargs)
            else:
                raise NotImplementedError(f"Method {method} is not implemented in GotAdapter.")
        else:
            # Pass all arguments to the parent CloudScraper class
            return super().request(method, url, *args, **kwargs)

    def get(self, url, referer='https://www.google.com/', *args, **kwargs):
        headers = kwargs.get('headers', {})

        # Set the referrer only if it's not None and 'Referer' is not already set in headers
        if referer is not None and ('Referer' not in headers or 'referer' not in headers):
            headers['Referer'] = referer
            kwargs['headers'] = headers

        if self.use_stealth:
            # Use static methods of GotAdapter for making the request
            return GotAdapter.get(url, *args, **kwargs)
        else:
            # Pass all arguments to the parent CloudScraper class
            return super().get(url, *args, **kwargs)


    # Method to get bs4 object by passing a URL
    def bs4(self, url, *args, **kwargs):
        # Use the inherited get method from CloudScraper to fetch the page content
        response = self.get(url, *args, **kwargs)
        
        # Check if the request was successful
        if response.status_code == 200:
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

