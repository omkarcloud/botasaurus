---
sidebar_position: 40
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
    browser_config = BrowserConfig(user_agent=UserAgent.user_agent_106, window_size=WindowSize.window_size_1280_720, profile=1)
```


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

LEt's say want to run many tasks then just name them one after another. example
```
python main.py linkedin_signup linkedin_post
```
in this case linkedin_signup task wiol be run and then linkedin_post task
