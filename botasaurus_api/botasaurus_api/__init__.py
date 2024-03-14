import requests
from requests.exceptions import ConnectionError

DEFAULT_API_URL = "http://127.0.0.1:8000"

class ApiException(Exception):
     pass

class Api:
    def __init__(self, api_url: str | None = None) -> None:
        """
        Initializes the API client with a specified server URL.

        :param api_url: The base URL for the API server. If not specified, defaults to "http://127.0.0.1:5000".
        """
        self.api_url = (api_url or DEFAULT_API_URL).rstrip("/")
        if not self.healthcheck():
            raise ApiException(f"API at {self.api_url} is not running. Please check if the API is up and running.")

    def make_api_url(self, path):
        return f"{self.api_url}/{path.rstrip("/")}"

    def healthcheck(self) -> bool:
        """
        Perform a health check on the "/api" endpoint.

        Returns:
            bool: True if the health check is successful, False otherwise.
        """
        try:
            response = requests.get(self.make_api_url("api"))
            # Check if the response status code is 200 (OK)
            return response.status_code == 200
        except ConnectionError:
            raise ApiException("""API at {} is not running. 
Check the network connection, or verify if the API is running on a different endpoint. In case the API is running on a different endpoint, you can pass the endpoint as follows:
api = Api('https://example.com')""".format(self.api_url))

# To following api client add a method called healthcheck which healtchecks "/api". Add comments also.
# Above is useful Prompt to make the client
