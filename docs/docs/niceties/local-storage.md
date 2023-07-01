---
sidebar_position: 60
---

# Local Storage

You can use the LocalStorage module to persist data across multiple Selenium Runs.

## Usage

The following example demonstrates the common methods used in the LocalStorage module:

```python
from bose import LocalStorage

# Set an item in the local storage
LocalStorage.set_item('username', 'johndoe')

# Retrieve an item from the local storage
username = LocalStorage.get_item('username')

# Remove an item from the local storage
LocalStorage.remove_item('username')

# Clear all items from the local storage
LocalStorage.clear()
```

## Use Case

LocalStorage is particularly useful when you need to share data between two tasks.

Let's consider an example where we have created a Google Maps Scraper with two tasks:

1. `scrape_links`: A task that scrapes Google Maps links for a specific search query.
2. `scrape_pages`: A task that visits each Google Maps link and extracts details such as business name, website, address, and phone number.

Now, to send the links from `scrape_links` to `scrape_pages`, we can save the links in `scrape_links` and retrieve them in `scrape_pages` using the LocalStorage module as follows:

`scrape_links`
```python
from bose import *

class Task(BaseTask):
    def run(self, driver):
        # ... Code to scrape Google Maps links
        LocalStorage.set_item('links', scraped_links)
```

`scrape_pages`
```python
from bose import *

class Task(BaseTask):
    def run(self, driver):
        scraped_links = LocalStorage.get_item('links')
        # ... Code to visit links and scrape Google Maps data
```