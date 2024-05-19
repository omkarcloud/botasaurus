from threading import Thread
import requests
import traceback
import time
import random
from .cleaners import clean_data
from .server import Server

def make_request_with_retry(request_lambda, max_retries=6, initial_delay=1, backoff_factor=2, max_delay=60):
    retries = -1
    delay = initial_delay

    while retries < max_retries:
        try:
            response = request_lambda()  # Call the lambda function
            response.raise_for_status()  # Raise an exception for HTTP error codes

            return response  # or return some result from processing

        except Exception as e:
            retries += 1

            if not (retries < max_retries):
                raise

            print(f"Attempt {retries + 1} failed with error: {e}. Retrying in {delay} seconds...")

            time.sleep(delay)
            delay = min(delay * backoff_factor, max_delay) + random.uniform(0, 0.1 * delay)  # Adding jitter

class WorkerExecutor():
    def load(self):
        pass

    def start(self):
        pass
    
    def run_worker_task(self, task, node_name):
        Thread(target=self.perform_worker_task, args=(task, node_name,), daemon=True).start()

    def perform_worker_task(self, task, node_name):
        scraper_type = task["scraper_type"]
        task_id = task["id"]
        scraper_name = task["scraper_name"]
        metadata = {"metadata": task["metadata"]} if task["metadata"] != {} else {}
        task_data = task["data"]

        fn = Server.get_scraping_function(scraper_name)

        try:
            result = fn(
                task_data,
                **metadata,
                parallel=None,
                cache=False,
                beep=False,
                run_async=False,
                async_queue=False,
                raise_exception=True,
                close_on_crash=True,
                output=None,
                create_error_logs=False
            )
            result = clean_data(result)
            make_request_with_retry(lambda: requests.post('http://master-srv:8000/k8s/success', json={"task_id": task_id, "task_type" : scraper_type,  "task_result": result , "node_name": node_name}))
        except Exception:
            exception_log = traceback.format_exc()
            traceback.print_exc()
            make_request_with_retry(lambda: requests.post('http://master-srv:8000/k8s/fail', json={"task_id": task_id, "task_type" : scraper_type,  "task_result": exception_log , "node_name": node_name}))
