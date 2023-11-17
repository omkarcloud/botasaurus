from cloudscraper import CloudScraper
from bs4 import BeautifulSoup


# Create a subclass of CloudScraper
class AntiDetectRequests(CloudScraper):
    
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
