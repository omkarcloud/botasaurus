---
sidebar_position: 20
---
# Browser Config

`BrowserConfig` is used to create an object that contains configuration options for a web browser that is run in the task. The following are the parameters of the constructor:

-   `user_agent`: A string that specifies the user agent of the web browser. By default a random user agent is selected on each run.
-   `window_size`: A List of integers representing window size of browser. By default it will use a `[1920, 1080]` Window Size.
-   `profile`: An string representing the profile of the web browser. By default no profile is used meaning the browser is like new with no history each time task is run. 
-   `use_undetected_driver`: A boolean value that specifies whether to use an undetected driver or not. Default value is `False` which means it will not use undetected driver. You may want to set it to `True` in case you are automating sites protected by Services like Cloudflare. 
-   `is_eager`: A boolean value that specifies whether to eagerly start selecting elements before the page has loaded completely. Default value is `False` meaning that it will wait for pages to load before selecting elements. You may want to set it to `True` in case the page is taking a long time to load but elements are selectable.

Usage
-----
You can set browser_config property on Task to specify the Browser Config as shown in below example

```python
from bose import BaseTask, BrowserConfig, WindowSize

class Task(BaseTask):
    browser_config = BrowserConfig(user_agent=UserAgent.user_agent_106, window_size=WindowSize.window_size_1280_720, profile=1, use_undetected_driver=True, close_on_crash=False)
```
