# Botasaurus API

The Botasaurus API client is a Python library for interacting with Botasaurus Scrapers via an API. 

It provides a simple and convenient way to create, fetch, download, abort, and delete tasks, as well as manage their results.

## Installation

To install the API client, use pip:

```bash
python -m pip install --upgrade botasaurus-api
```

## Usage

First, import the `Api` class from the library:

```python
from botasaurus-api import Api
```

Then, create an instance of the `Api` class:

```python
api = Api()
```

You can also provide an optional `api_url` parameter to specify the base URL for the API server. If the `api_url` parameter is not provided, it defaults to `http://localhost:8000`.

```python
api = Api('https://example.com/')
```

Additionally, the API client will create response JSON files in the `output/responses/` directory to help with debugging and development. If you want to disable this feature in production, you can set `create_response_files=False`.

```python
api = Api(create_response_files=False)
```

### Creating Tasks

There are two types of tasks:

- Asynchronous Task
- Synchronous Task

Asynchronous tasks run asynchronously, without waiting for the task to be completed. The server will return a response immediately, containing information about the task, but not the actual results. The client can then retrieve the results later.

Synchronous tasks, on the other hand, wait for the completion of the task. The server response will contain the results of the task.

You should use asynchronous tasks when you want to run a task in the background and retrieve the results later. Synchronous tasks are better suited for scenarios where you have a small number of tasks and want to wait and get the results immediately.

To create an asynchronous task, use the `create_async_task` method:

```python
data = {'link': 'https://www.omkar.cloud/'}
task = api.create_async_task(data)
```

You can also provide an optional `scraper_name` parameter to specify the scraper to be used for the task, if not provided, it will use the default scraper:

```python
task = api.create_async_task(data, scraper_name='scrape_heading_task')
```

To create a synchronous task, use the `create_sync_task` method:

```python
data = {'link': 'https://www.omkar.cloud/blog/'}
task = api.create_sync_task(data)
```

You can create multiple asynchronous or synchronous tasks at once using the `create_async_tasks` and `create_sync_tasks` methods, respectively:

```python
data_items = [{'link': 'https://www.omkar.cloud/'}, {'link': 'https://www.omkar.cloud/blog/'}]
tasks = api.create_async_tasks(data_items)
tasks = api.create_sync_tasks(data_items)
```

### Fetching Tasks

To fetch tasks from the server, use the `get_tasks` method:

```python
tasks = api.get_tasks()
```

By default, all tasks are returned. You can also apply pagination, views, sorts and filters:

```python
tasks = api.get_tasks(
    page=1,
    per_page=10,
    # view='overview',
    # sort='my-sort',
    # filters={'your_filter': 'value'},
)
```

To fetch a specific task by its ID, use the `get_task` method:

```python
task = api.get_task(task_id=1)
```

### Fetching Task Results

To fetch the results of a specific task, use the `get_task_results` method:

```pytho
results = api.get_task_results(task_id=1)
```

You can also apply views, sorts and filters:

```python
results = api.get_task_results(
    task_id=1,
    page=1,
    per_page=20,
    # view='overview',
    # sort='my_sort',
    # filters={'your_filter': 'value'},
)
```

### Downloading Task Results

To download the results of a specific task in a particular format, use the `download_task_results` method:

```python
results_bytes, filename = api.download_task_results(task_id=1, format='csv')
with open(filename, 'wb') as file:
    file.write(results_bytes)
```

You can also apply views, sorts and filters:

```python
results_bytes, filename = api.download_task_results(
    task_id=1,
    format='excel',  # format can be one of: json, csv or excel
    # view='overview',
    # sort='my_sort',
    # filters={'your_filter': 'value'},
)
```

### Aborting and Deleting Tasks

To abort a specific task, use the `abort_task` method:

```python
api.abort_task(task_id=1)
```

To delete a specific task, use the `delete_task` method:

```python
api.delete_task(task_id=1)
```

You can also bulk abort or delete multiple tasks at once using the `abort_tasks` and `delete_tasks` methods, respectively:

```python
api.abort_tasks(1, 2, 3)
api.delete_tasks(4, 5, 6)
```

## Examples

Here are some example usages of the API client:

```python
from botasaurus_api import Api

# Create an instance of the API client
api = Api()

# Create an asynchronous task
data = {'link': 'https://www.omkar.cloud/'}
task = api.create_sync_task(data, scraper_name='scrape_heading_task')

# Fetch the task
task = api.get_task(task['id'])

# Fetch the task results
results = api.get_task_results(task['id'])

# Download the task results as a CSV
results_bytes, filename = api.download_task_results(task['id'], format='csv')

# Abort the task
api.abort_task(task['id'])

# Delete the task
api.delete_task(task['id'])

# --- Bulk Operations ---

# Create multiple synchronous tasks
data_items = [{'link': 'https://www.omkar.cloud/'}, {'link': 'https://www.omkar.cloud/blog/'}]
tasks = api.create_sync_tasks(data_items, scraper_name='scrape_heading_task')

# Fetch all tasks
all_tasks = api.get_tasks()

# Bulk abort tasks
api.abort_tasks(*[task['id'] for task in tasks])

# Bulk delete tasks
api.delete_tasks(*[task['id'] for task in tasks])
```

## That's It!

Now, go and build something awesome.