---
sidebar_position: 50
---

# Bose Driver

The driver you receive in the **`run`** method of the Task is an extended version of Selenium that adds powerful methods to make working with Selenium much easier. Some of the popular methods added to the Selenium driver by Bose Framework are:

| METHOD | DESCRIPTION |
| --- | --- |
| get_by_current_page_referrer(link, wait=None) | simulate a visit that appears as if you arrived at the page by clicking a link. This approach creates a more natural and less detectable browsing behavior. |
| js_click(element) | enables you to click on an element using JavaScript, bypassing any interceptions(ElementClickInterceptedException) from pop-ups or alerts |
| get_cookies_and_local_storage_dict() | returns a dictionary containing "cookies" and "local_storage” |
| add_cookies_and_local_storage_dict(self, site_data) | adds both cookies and local storage data to the current web site |
| organic_get(link, wait=None) | visits google and then visits the “link” making it less detectable |
| local_storage | returns an instance of the LocalStorage module for interacting with the browser's local storage in an easy to use manner |
| save_screenshot(filename=None) | save a screenshot of the current web page to a file in tasks/ directory |
| short_random_sleep() and long_random_sleep(): | sleep for a random amount of time, either between 2 and 4 seconds (short) or between 6 and 9 seconds (long) |
| get_element_or_* [eg: get_element_or_none, get_element_or_none_by_selector, get_element_by_id, get_element_or_none_by_text_contains,] | find web elements on the page based on different criteria. They return the web element if it exists, or None if it doesn't. |
| is_in_page(target, wait=None, raise_exception=False) | checks if the browser is in the specified page |
