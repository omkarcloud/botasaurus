---
sidebar_position: 25
---
# Browser and Task Config

## Browser Config

In bare Selenium, if you want to configure options such as the profile, user agent, or window size, it requires writing a lot of code, as shown below:

```python
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

driver_path = 'path/to/chromedriver.exe'

options = Options()

profile_path = '1'

options.add_argument(f'--user-data-dir={profile_path}')

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.37")'
options.add_argument(f'--user-agent={user_agent}')

window_width = 1200
window_height = 720
options.add_argument(f'--window-size={window_width},{window_height}')

driver = webdriver.Chrome(executable_path=driver_path, options=options)
```

On the other hand, Bose Framework simplifies these complexities by encapsulating the browser configuration within the **`BrowserConfig`** property of the Task, as shown below:

```python
from bose import BaseTask, BrowserConfig, UserAgent, WindowSize

class Task(BaseTask):
    browser_config = BrowserConfig(user_agent=UserAgent.user_agent_106, window_size=WindowSize.window_size_1280_720, )
```


Also, We have introduced an incredible feature called Tiny Profile. Unlike the Traditional Chrome Profile, which can easily reach a size of 100 MB, the Tiny Profile significantly reduces profile sizes. By persisting the cookies of each website you visit within the browser session, the Tiny Profile achieves profile sizes of approximately 1 KB.

What does this mean for you? Well, suppose you need to create 1000 accounts on a website. With the Tiny Profile, you can store the information for all 1000 accounts in just 1 MB of storage.

Below is an example of how to utilize the Tiny Profile feature in your code:

```python
from bose import *

class Task(BaseTask):
    browser_config = BrowserConfig(profile=1, is_tiny_profile=True)
```

By setting `is_tiny_profile` to `True` in the `BrowserConfig` object, you can take advantage of the Tiny Profile functionality. This will allow you to efficiently manage and store large amounts of account data within a minimal amount of storage space.



## Task Config

<!-- `change_ip_on_start` (default: false)
Prompts to Change IP when task is started -->

`prompt_to_close_browser` (default: false)
Prompts to close target site if open in other browsers to evade bot detection

`change_ip` (default: false)
Prompts to change IP before, in between and end of Task. 

`beep` (default: true)
beeps when prompted, when task finished, or when there is error. 
if in office setting to not distriub people set to false. 

`output_filename`
File name you want to save the putput returned from run.

`close_on_crash`
A boolean value that specifies whether to close the browser window on crash or not. Default value is `False` meaning that it will prompt the user to press enter to close the browser.

### Good Config for Bot Creation Tasks is 


```python
from bose import BaseTask, TaskConfig

class Task(BaseTask):
    task_config = TaskConfig(prompt_to_close_browser=True, change_ip=True)
```

## Running Tasks

If you wish to execute multiple sequentially, you can specify them in the `config.py` file as follows:

```python
from .linkedin_signup import LinkedinSignupTask
from .linkedin_post import LinkedinPostTask

tasks_to_be_run = [
    LinkedinSignupTask,
    LinkedinPostTask
]
```

To run these tasks, you can use the following command:

```shell
python main.py
```
