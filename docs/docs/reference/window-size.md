---
sidebar_position: 40
---
# Window Size

The WindowSize provides a set of commonly used pre-defined window sizes for web browsers. It also provides two class-level constants, RANDOM and HASHED.

Class Attributes
----------------

-   `RANDOM`: A string constant that can be used to indicate a randomly selected window size. When using the RANDOM window size, we mimic real-world window sizes in a way that the probability of getting a window size is consistent with real-world usage. This behavior aligns with your expectations.
-   `HASHED`: A string constant that can be used to indicate a hashed window size based on the profile passed to BrowserConfig. When using the HASHED window size, we mimic real-world window sizes in a way that the probability of getting a window size is consistent with real-world usage. This behavior aligns with your expectations.
-   `window_size_1920_1080`: A list of integers representing the dimensions of a browser window of size 1920x1080 pixels.
-   `window_size_1366_768`: A list of integers representing the dimensions of a browser window of size 1366x768 pixels.
-   `window_size_1536_864`: A list of integers representing the dimensions of a browser window of size 1536x864 pixels.
-   `window_size_1280_720`: A list of integers representing the dimensions of a browser window of size 1280x720 pixels.
-   `window_size_1440_900`: A list of integers representing the dimensions of a browser window of size 1440x900 pixels.
-   `window_size_1600_900`: A list of integers representing the dimensions of a browser window of size 1600x900 pixels.
Window Size class is used to denote the window size to use when running the browser. The default Window Size is 1920x1080. 

Usage
-----
WindowSize in used when specifying the BrowserConfig in Task. 

For example the following example specifies to use a random WindowSize instead of the default `1920x1080`.

```python
from bose import BaseTask, BrowserConfig, WindowSize

class Task(BaseTask):
    browser_config = BrowserConfig(window_size=WindowSize.RANDOM)
```

Note that in case you do not specify window_size By default the Task in ran with default WindowSize of `1920x1080`.