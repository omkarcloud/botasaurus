import requests
from requests.exceptions import ConnectionError

class ApiException (Exception):
     pass

class Api:
    def __init__(self, api_url: str | None = None) -> None:
        """
        Initializes the API client with a specified server URL.
        :param api_url: The base URL for the API server. If not specified, defaults to "http://127.0.0.1:5000".
        """
        DEFAULT_API_URL = "http://127.0.0.1:8000"
        self.api_url = (api_url or DEFAULT_API_URL).rstrip("/")
        if not self.is_api_running():
            raise ApiException(f"API at {self.api_url} is not running. Please check if the API is up and running.")

    def make_api_url(self, path):
        return f"{self.api_url}/{path}"

    def is_api_running(self) -> bool:
        """
        Checks if the API is running by performing a health check on the "/api" endpoint.

        :return: True if the health check is successful, otherwise False.
        """
        try:
            response = requests.get(self.make_api_url("api"))
            # Check if the response status code is 200 (OK)
            return response.status_code == 200
        except ConnectionError:
            raise ApiException("""API at {} is not running. 
Check the network connection, or verify if the API is running on a different endpoint. In case the API is running on a different endpoint, you can pass the endpoint as follows:
api = Api('https://example.com')""".format(self.api_url))

    def create_async_task(self, data, scraper_name=None):
        """
        Submits an asynchronous task to the server.

        :param data: The data to be processed by the task.
        :param scraper_name: The name of the scraper to use for the task. If not provided, the server will use the default scraper.
        :return: The created task object.
        """
        url = self.make_api_url("api/tasks/create-task-async")
        payload = {
            "data": data,
            "scraper_name": scraper_name,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_sync_task(self, data, scraper_name=None):
        """
        Submits a synchronous task to the server.

        :param data: The data to be processed by the task.
        :param scraper_name: The name of the scraper to use for the task. If not provided, the server will use the default scraper.
        :return: The created task object.
        """
        url = self.make_api_url("api/tasks/create-task-sync")
        payload = {
            "data": data,
            "scraper_name": scraper_name,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_async_tasks(self, data_items, scraper_name=None):
        """
        Submits multiple asynchronous tasks to the server in a batch.

        :param tasks: A list of dictionaries, each containing the scraper's input data.
        :param scraper_name: The name of the scraper to use for the tasks. If not provided, the server will use the default scraper.
        :return: A list of created task objects.
        """
        url = self.make_api_url("api/tasks/create-task-async")
        # Prepare the payload as a list of tasks, each with its data and optional scraper_name
        payload = [{"data": data, "scraper_name": scraper_name} for data in data_items]
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_sync_tasks(self, data_items, scraper_name=None):
        """
        Submits multiple synchronous tasks to the server in a batch and waits for the results.

        :param tasks: A list of dictionaries, each containing the scraper's input data.
        :param scraper_name: The name of the scraper to use for the tasks. If not provided, the server will use the default scraper.
        :return: A list of created task objects, each with its processing result.
        """
        url = self.make_api_url("api/tasks/create-task-sync")
        # Prepare the payload as a list of tasks, each with its data and optional scraper_name
        payload = [{"data": data, "scraper_name": scraper_name} for data in data_items]
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_tasks(self, page=None, per_page=None, with_results=True):
        """
        Fetches tasks from the server, with optional result inclusion, pagination, and filtering.

        :param page: The page number for pagination.
        :param per_page: The number of tasks to return per page.
        :param with_results: Whether to include the task results in the response.
        :return: A dictionary containing the task results and pagination information.
        """
        url = self.make_api_url("api/tasks")
        params = {
            "with_results": str(with_results).lower(),
        }
        if page is not None:
            params["page"] = str(page)
        if per_page is not None:
            params["per_page"] = str(per_page)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id):
        """
        Retrieves a specific task by ID.

        :param task_id: The ID of the task to retrieve.
        :return: The task object.
        """
        url = self.make_api_url(f"api/tasks/{task_id}")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_results(self, task_id, filters=None, sort=None, view=None, page=1, per_page=None):
        """
        Retrieves the results of a specific task.

        :param task_id: The ID of the task.
        :param filters: A dictionary of filters to apply to the task results, optional.
        :param sort: The sort to apply to the task results, optional.
        :param view: The view to apply to the task results, optional.
        :param page: The page number to retrieve, default is 1. 
        :param per_page: The number of results to return per page. If per_page is not provided, all results are returned, optional.

        :return: A dictionary containing the task results and pagination information if page and per_page are provided.
        """
        url = self.make_api_url(f"api/tasks/{task_id}/results")
        payload = {}
        if filters:
            payload["filters"] = filters
        if sort:
            payload["sort"] = sort
        if view:
            payload["view"] = view
        if page:
            payload["page"] = page
        if per_page:
            payload["per_page"] = per_page
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def download_task_results(self, task_id, format=None, filters=None, sort=None, view=None, convert_to_english=True):
        """
        Downloads the results of a specific task in the specified format.

        :param task_id: The ID of the task.
        :param format: The format to download the task results in. Available formats are "json", "csv", "excel". The default format is "json".
        :param filters: A dictionary of filters to apply to the task results, optional.
        :param sort: The sort to apply to the task results, optional.
        :param view: The view to apply to the task results, optional.
        :param convert_to_english: Whether to convert the task results to English, default is True, optional.

        :return: The downloaded task results in the specified format as bytes.
        """
        payload = {}
        if format:
            payload["format"] = format
        if filters:
            payload["filters"] = filters
        if sort:
            payload["sort"] = sort
        if view:
            payload["view"] = view
        if convert_to_english:
            payload["convert_to_english"] = convert_to_english

        url = self.make_api_url(f"api/tasks/{task_id}/download")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.content

    def abort_task(self, task_id):
        """
        Aborts a specific task.

        :param task_id: The ID of the task to abort.
        :return: A success message.
        """
        url = self.make_api_url(f"api/tasks/{task_id}/abort")
        response = requests.patch(url)
        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id):
        """
        Deletes a specific task.

        :param task_id: The ID of the task to delete.
        :return: A success message.
        """
        url = self.make_api_url(f"api/tasks/{task_id}")
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()

    def delete_tasks(self, task_ids):
        """
        Bulk deletes tasks.

        :param task_ids: A list of task IDs to be deleted.
        :return: A success message.
        """
        url = self.make_api_url("api/tasks/bulk-delete")
        payload = {"task_ids": task_ids}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def abort_tasks(self, task_ids):
        """
        Bulk aborts tasks.

        :param task_ids: A list of task IDs to be aborted.
        :return: A success message.
        """
        url = self.make_api_url("api/tasks/bulk-abort")
        payload = {"task_ids": task_ids}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
