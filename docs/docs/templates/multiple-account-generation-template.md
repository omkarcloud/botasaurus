# Multiple Account Generation Template 

This Web Scraping Template provides you with a great starting point when creating multiple accounts on a website.

## 🚀 Getting Started

1️⃣ Clone the Magic 🧙‍♀️:
```shell
git clone https://github.com/omkarcloud/multiple-account-generation-template
cd multiple-account-generation-template
```

2️⃣ Install Dependencies 📦:
```shell
python -m pip install -r requirements.txt
```

3️⃣ Write Code to Generate Multiple Accounts on the Target Website. 🤖

4️⃣ Run Bot 😎:

```shell
python main.py
```

## ✨ Best Practices for Account Generation

When creating a large number of bot accounts on a website, it is recommended to follow these best practices:

1. Clear Storage and Change IP

   Websites like LinkedIn track user IPs, and if they detect that the IP used for the bot account matches the one used for the real LinkedIn account, it raises suspicions of multiple account creation and mostly results in the restriction of your account. 
   
   ![LinkedIn Restricted Account](/img/linkedin-restricted.png)

   They typically do not provide a specific reason for the suspension, as it prevents users from learning what tactics work and what doesn't, which would lead to more resilient bots.

   To prevent such suspensions and ensure there is no linkage between your bot accounts and real accounts, follow these steps.

   1. Clear the storage of the target website in all browsers where you have visited the site or have an account. This will log you out from the website.

   ![Clear Storage](/img/clear-storage.gif)


   2. Close browsers.

   3. Change your IP following the "Mobile Aeroplane Method" described in the "Changing IP" lesson.

2. Ensure unique IPs for each bot. After automating actions with one bot, change the IP before using another bot. You can use the following config in Task to prompt you to change IP.
```python
from bose import BaseTask, TaskConfig

class Task(BaseTask):
    task_config = TaskConfig(prompt_to_close_browser=True, change_ip=True)
```

And change the IP following the "Mobile Aeroplane Method" described in the "Changing IP" lesson.

3. Use a profile to maintain the state of the browser session between runs. You can achieve this by configuring the browser as follows:

```python
class Task(BaseTask):
    browser_config = BrowserConfig(profile='1', is_tiny_profile=True)
```

4. Make the bot look humane by adding random waits. You can use the `driver.short_random_sleep` and `driver.long_random_sleep` methods for it. 

5. Use a real-looking name, email, username, and password generated using the [Account Generator Module](../../niceties/account-generator/).

To see these best practices in action, I highly recommend reviewing the code of the Outlook account creator bot provided [here](https://github.com/omkarcloud/outlook-account-generator/blob/master/src/outlook_sign_up_task.py).

