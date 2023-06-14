---
sidebar_position: 10
---
# Bose Driver

Bose Driver extends the functionality of the Selenium webdriver to make more easier to use for Website Automation and Scraping. 

Let's go through the various methods available in the class and their usage:

1.  `get_by_current_page_referrer(link, wait=None)`:


An alternative to `driver.get` is the `get_by_current_page_referrer(link, wait=None)` utility. When using `driver.get`, the `document.referrer` property remains empty, indicating that you directly entered the page URL in the search bar, which can raise suspicion for bot detection systems.

By employing `get_by_current_page_referrer(link, wait=None)`, you can simulate a visit that appears as if you arrived at the page by clicking a link. This approach creates a more natural and less detectable browsing behavior.

In general, when navigating to an internal page of a website, it is recommended to replace `driver.get` with `get_by_current_page_referrer`. Additionally, you have the option to specify the amount of time to wait before navigating, using the optional `wait` parameter.


```python
driver.get_by_current_page_referrer("https://example.com")
```

2.  `js_click(element)`: 

While clicking elements with Selenium, elements can be intercepted by pop-ups, alerts, or other elements, leading to the raising of an **`ElementClickInterceptedException`** error.

To handle such situations, you can utilize the **`js_click`** method. This method enables you to click on an element using JavaScript, bypassing any interceptions from pop-ups or alerts. 

By employing the **`js_click`** method, you can ensure that the click operation is executed smoothly without being intercepted. 



```python
button = driver.get_element_or_none_by_selector(".button")
driver.js_click(button)
```

3.  `sleep(n)`: 



This method pauses the execution of the script for `n` seconds. You can use it like this:



```python
driver.sleep(10)  # sleep for 10 seconds
```

4.  `wait_for_enter()`: 



This method waits for the user to press the Enter key to continue. You can use it like this:


```python
driver.wait_for_enter()
```

5.  `short_random_sleep()` and `long_random_sleep()`: 

These methods sleep for a random amount of time, either between 2 and 4 seconds (short) or between 6 and 9 seconds (long). You can use them like this:



```python
driver.short_random_sleep()
driver.long_random_sleep()
```

6.  `sleep_forever()`: 

This method puts the script to sleep indefinitely. You can use it like this:



```python
driver.sleep_forever()
```

7.  `get_bot_detected_by()` and `is_bot_detected()`: 

These methods detect if a bot detection page is being displayed. `get_bot_detected_by()` returns the type of bot detection page, while `is_bot_detected()` returns a boolean indicating whether a bot detection page is being displayed. You can use them like this:



```python
if driver.is_bot_detected():
    print(f"Bot detected by {driver.get_bot_detected_by()}")
```

8.  `get_element_or_none(xpath, wait=None)`, `get_element_or_none_by_selector(selector, wait=None)`, `get_element_by_id(id, wait=None)`, `get_element_or_none_by_text_contains(text, wait=None)`, `get_element_or_none_by_text(text, wait=None)`,  `get_element_or_none_by_name(selector, wait=None)`: 

These methods find web elements on the page based on different criteria. They return the web element if it exists, or `None` if it doesn't. You can also pass number of seconds to wait for element to appear. You can use them like this:



```python
# find an element by xpath
element = driver.get_element_or_none("//div[@class='example']", 4)

# find an element by CSS selector
element = driver.get_element_or_none_by_selector(".example-class", 4)

# find an element by ID
element = driver.get_element_by_id("example-id", 4)

# find an element by text
element = driver.get_element_or_none_by_text("Example text", 4)

# find an element by partial text
element = driver.get_element_or_none_by_text_contains("Example", 4)

# find an element with attribute name = "email"
element = driver.get_element_or_none_by_name("email", 4)
```

9.  `get_elements_or_none_by_selector(selector, wait=None)`: 



This method finds multiple web elements on the page based on a CSS selector. It returns a list of web elements, or `None` if none are found. You can use it like this:



```python
# find all div elements with class "example"
elements = driver.get_elements_or_none_by_selector("div.example")
```

10.  `get_element_text(element)` and `get_innerhtml(element)`: 



These methods get the text or HTML content of a web element. You can use them like this:


```python
text = driver.get_element_text(element)
html = driver.get_innerhtml(element)
```

11. `get_element_parent(element)`:

This method returns the parent element of a given web element.

```python
parent_element = BoseDriver.get_element_parent(element)
```

12. `scroll_site()`:

This method scrolls the current webpage.

```python
driver.scroll_site()
```

13. `scroll_element(element)`:

This method scrolls a given web element. It first checks if the element has been scrolled to the end, and if it has, it returns False. Otherwise, it scrolls the element and returns True.


```python
driver.scroll_element(element)
``` 

14. `get_cookies_dict()`:

This method returns a dictionary of cookies for the current webpage as a key value dict. 

```python
cookies_dict = driver.get_cookies_dict()
```

15. `get_local_storage_dict()`:

This method returns a dictionary of key-value pairs for the local storage of the current webpage. 

```python
local_storage_dict = driver.get_local_storage_dict()
```

16. `get_cookies_and_local_storage_dict()`:

This method returns a dictionary containing two keys, "cookies" and "local_storage", each of which contains a dictionary of the cookies and local storage. You can use them to persist session by storing them in a JSON file.

```python
site_data = driver.get_cookies_and_local_storage_dict()
```

17. `add_cookies_dict(cookies)`:

```python
cookies_dict = {"name": "value"}
driver.add_cookies_dict(cookies_dict)
``` 

18. `add_local_storage_dict(local_storage)`:

This method adds key-value pairs to the local storage of the current webpage. It takes a dictionary of key-value pairs as input

```python
local_storage = {"name": "John", "age": 30}
driver.add_local_storage_dict(local_storage)
```

This will add the key-value pairs `{"name": "John", "age": 30}` to the local storage of the web page loaded in the `driver`.

19.  `add_cookies_and_local_storage_dict(site_data)`:

This method adds both cookies and local storage data to the current web site.

Example:

```python
site_data = {
    "cookies": {"cookie1": "value1", "cookie2": "value2"},
    "local_storage": {"name": "John", "age": 30}
}
driver.add_cookies_and_local_storage_dict(site_data)
```

This will add the cookies `{"cookie1": "value1", "cookie2": "value2"}` and the local storage data `{"name": "John", "age": 30}` to the web page loaded in the `driver`.

20.  `delete_cookies_dict()`:

This method deletes all cookies from the current web page.

Example:

```python

driver.delete_cookies_dict()
```

This will delete all cookies from the web page loaded in the `driver`.

21.  `delete_local_storage_dict()`:

This method clears the local storage of the current web page.

Example:

```python
driver.delete_local_storage_dict()
```

This will clear the local storage of the web page loaded in the `driver`.

22.  `delete_cookies_and_local_storage_dict()`:

This method calls `delete_cookies_dict()` and `delete_local_storage_dict()` methods internally to delete both cookies and local storage data from the current web page.

Example:

```python
driver.delete_cookies_and_local_storage_dict()
```

This will delete both cookies and local storage data from the web page loaded in the `driver`.

23.  `organic_get(link, wait=None)`:

This method follows a two-step process: it first loads the Google homepage and then navigates to the specified link. This approach closely resembles the way people typically visit websites, resulting in more humane behavior and reduces chances of bot being detected.

-   `link`: the URL to navigate to.

Example:

```python
driver.organic_get("https://example.com")
```

This will navigate to `https://example.com` by setting the referrer to the Google homepage.

24.  `get_google()`:

This method loads the Google homepage.

Example:


```python
driver.get_google()
```


25.  `local_storage`

This property returns an instance of the `LocalStorage` class from the `bose.drivers.local_storage` module. This class is used for interacting with the browser's local storage in an easy to use manner.

Usage:

```python

local_storage = driver.local_storage

# Set an item in the Browser's Local Storage
local_storage.set_item('username', 'johndoe')

# Retrieve an item from the Browser's Local Storage
username = local_storage.get_item('username')

```

26.  `get_links(search=None, wait=None)`

This method retrieves all the links on the current web page and returns a list of links that match a search string (if provided).
Usage:

```
links = driver.get_links()
```
27.  `get_images(search=None, wait=None)`

This method retrieves all the images on the current web page and returns a list of links to the images that match a search string (if provided).

Usage:

```
images = driver.get_images()
```

28.  `is_in_page(target, wait=None, raise_exception=False)`

This method checks if the browser is in the specified page. It will keep checking the URL for a specified amount of time (if wait is provided) and return False if the target is not found. If raise_exception is True, it will raise an exception if the page is not found.

Usage:

```
is_in_page = driver.is_in_page('example.com', wait=10, raise_exception=True)
```

29.  `save_screenshot(filename=None)`

This method saves a screenshot of the current web page to a file in `tasks/` directory. The filename of the screenshot is generated based on the current date and time, unless a custom filename is provided.

Usage:

```
driver.save_screenshot()
```