---
sidebar_position: 3
---

# Sign Up Tutorial

## 🏗️ What Are We Building?

In this Tutorial, we're doing something you've likely done many times before: signing up for a website.

However, this time, we're using bots. This empowers us, as developers, to create thousands of accounts on a website in an automated manner, granting us great power.

![](/img/sign-up-bot-running.gif)

## 🤔 Why are we building it?

The power of bots is immense. With hundreds of bots at your command:

- You can mass message thousands of people on platforms like Twitter, LinkedIn, or Reddit to promote your product.

- Platforms like MailChimp offer free plans with limited usage. With bots, you can maximize the benefits of these plans. For instance, if MailChimp allows you to send 500 emails per month for free, with 100 bots, you can send 50,000 emails monthly.

This tutorial will guide you through creating multiple accounts on the Omkar Cloud website with email verification.

And the best part? You'll do it in less than 100 lines of code using Botasaurus.

So, are you ready to build your bot army?

![](/img/robo-army.jpg)

Let's get started :)

<!-- ## 💡 Understanding Botasaurus

Before we dive into creating a Sign Up Bot, let's quickly grasp how Botasaurus works with a simple example.

In this simple example, we'll walk through the process of scraping the heading text from [https://www.omkar.cloud/](https://www.omkar.cloud/).

![](/img/starter-bot-running.gif)

### Step 1: Install Botasaurus

Start by installing Botasaurus with the help of this command:

```shell
python -m pip install botasaurus
```

### Step 2: Set Up Your Botasaurus Project

1. Create a directory for our Botasaurus project and navigate to it:

```shell
mkdir my-botasaurus-project
cd my-botasaurus-project
code .  # Optionally, open the project in VSCode
```

### Step 3: Write the Scraping Code

Within your project directory, create a Python script named `main.py` and paste the following code into `main.py`:

```python
from botasaurus.launch_tasks import launch_tasks
from botasaurus import *

# Define a custom scraping Task
class ScrapeHeadingTask(BaseTask):

    def run(self, driver: BotasaurusDriver, data):
        # Visit the Omkar Cloud website
        driver.get("https://www.omkar.cloud/")

        # Get the heading element text
        heading = driver.text("h1")
    
        # Return the data to be saved as a JSON file in output/all.json
        return {
            "heading": heading
        }

if __name__ == "__main__":
    # Launch the web scraping task
    launch_tasks(ScrapeHeadingTask)
```

Let's break down this code:

- We define a custom scraping task class named `ScrapeHeadingTask`.
```python
class ScrapeHeadingTask(BaseTask):
```  

- Inside the `run` method, we are automatically passed a Selenium driver by Botasaurus.
```python
    def run(self, driver: BotasaurusDriver, data):
```  

- In the `run` method:
    - We visit Omkar Cloud
    - Extract the heading text
    - Finally, return data to be saved as JSON and CSV files.
```python
    driver.get("https://www.omkar.cloud/")

    # Get the heading element text
    heading = driver.text("h1")
  
    # Return the data to be saved as a JSON file in output/all.json
    return {
        "heading": heading
    }
```  

- Lastly, we launch the scraping task.
```python
if __name__ == "__main__":
    # Launch the web scraping task
    launch_tasks(ScrapeHeadingTask)
```  

### Step 4: Run the Scraping Task

Now, let's run the bot:

```shell
python main.py
```

After running, the script will:
- Launch Google Chrome
- Visit [omkar.cloud](https://www.omkar.cloud/)
- Extract the heading text
- Automatically save it as `output/finished.json`.

![](/img/starter-bot-running.gif)

Now that you've successfully created a simple scraper, let's move on to creating a more solid Sign Up Bot :)
 -->

## 🛠️ How Are We Gonna Build That?

Our Bot is gonna take 3 simple Steps to create an Omkar Cloud Account:

1. Visiting Sign Up Page .
2. Filling and Submiting the Sign-Up Form.
3. Verifying the Email.

## ✍️ Signing Up

When creating a bot to sign up on a website, it's essential to ensure that the bot mimics human-like behavior as closely as possible.

This minimizes the chances of it being detected and flagged by bot detection companies like Cloudflare.

![](/img/captcha.png)

### Visiting the Sign-Up Page

To mimic human behavior, instead of directly visiting the Sign-Up Page via its link, it's recommended to first visit Google and then the website.

This makes it appear to the website that the user has arrived from a Google Search and *not by pasting a link*.

To achieve this organic navigation, we use the `organic_get` method as follows:

```python 
driver.organic_get("https://www.omkar.cloud/auth/sign-up/")
```

![](/img/organic-get.gif)

### Generating Account Information

For generating multiple accounts, you'll need names, emails, and passwords.

But where do you get these details?

A simple approach might be to use Python's random module:

```python 
name = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
email = ''.join(random.choice(string.ascii_lowercase) for i in range(6))  + "@gmail.com"
password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
```

This generates data like:

```
name = cnwyad
email = gvfqki@gmail.com
password = 3Eq8mK40
```

But wait, so the user's name will be `cnwyad`?

I've never met a person with a name `cnwyad`, and no parent in the world would name their kid `cnwyad`. Well, except maybe Elon Musk.

![](/img/elon-child-name.jpg)

Names like `XAEA-12 Musk` are likely to be flagged as bots and suspended by target websites, as LinkedIn often does.

![LinkedIn Restricted Account](/img/linkedin-restricted.png)

Instead of relying on purely random generation, we could use the Account Generator Module, which provides human-like data.

![Account](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/generated-account.png)

Accounts produced by the Account Generator Module are so humane that it's nearly impossible to detect whether the account belongs to a human or a bot.

The following code generates such accounts:

```python
account = bt.generate_user(country=bt.Country.IN)
        
name = account['name']
email = account['email']
password = account['password']
```

Now, let's enter the name, email, and password into the Sign-Up Form and submit it. Here's one way to do it using the traditional Selenium methods:


```python
name_input = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="name"]'))
)
name_input.send_keys(name)

email_input = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
)
email_input.send_keys(email)

password_input = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
)
password_input.send_keys(password)

sign_up_button = WebDriverWait(driver, 4).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))
)
sign_up_button.click()
```

However, this approach is verbose and prone to bugs. 

Thankfully, with the driver provided by Botasaurus, we can achieve the same logic in a cleaner manner as follows:

```python
driver.type('input[name="name"]', name)
driver.type('input[type="email"]', email)
driver.type('input[type="password"]', password)
driver.click('button[type="submit"]')
```

This method is not only cleaner but also smarter, as the `driver.type` and `driver.click` methods automatically wait for up to 4 seconds for the element to appear on the page, removing the need for explicit waits.

Because we are using bots, the form fills out so quickly that you might miss seeing it in action. 

To solve this, you can add the `driver.prompt` method at the end of the code. 

This pauses the browser, allowing you to inspect the page.

![](/img/pause-image.png)

To use the `driver.prompt` method, simply add:

```python
driver.prompt()
```

## ✅ Verify Email

A standard practice during the registration process on many websites, including omkar.cloud, is to send an email verification link to confirm the email's validity.

![](/img/signup-email.png)

To complete the sign-up, we must retrieve and open this link. But how can we do that?

Thankfully, Botasaurus comes to the rescue with its `TempMail` module. 

TempMail module allows us to create a temporary email address and receive emails.

To easily get the verification link and, as a best practice, delete the email afterward, we can use the `get_email_link_and_delete_mailbox` method as follows:

```python
link = bt.TempMail.get_email_link_and_delete_mailbox(email)
```

With the link in our hands, the final step is for our bot to visit it:

```python
driver.get(link)
```
## 💾 Persisting Sign-Up Sessions Using Profiles

Creating accounts is great, but if we don't persist the session in a Chrome profile, the account is lost after the browser closes.

### Using Chrome Profiles for Session Persistence

A solution to this issue is to persist the session using Chrome Profiles.

For those who have tried using Chrome Profiles with plain Selenium, know that the process can be cumbersome and often bug-prone. The code to use profiles in Selenium looks like this:

```python
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

driver_path = 'path/to/chromedriver.exe'

options = Options()
profile_path = 'my-profile'
options.add_argument(f'--user-data-dir={profile_path}')

driver = webdriver.Chrome(executable_path=driver_path, options=options)
```

### Botasaurus Simplifies Chrome Profiles

Botasaurus simplifies this process, making profile configuration straightforward. To use a profile, simply specify it in the decorator:

```python
@browser(profile='my-profile',)
def create_accounts(driver: AntiDetectDriver, account):
    ...
```

### Reducing Profile Size with `tiny_profile`

Regular Chrome Profiles can be heavy on storage. They can easily balloon to 100MBs after just a few runs, making it hard to store thousands of such profiles on your PC. 

Botasaurus offers a solution with its `tiny_profile` feature. It ensures only the cookies persist, slashing the profile size from the whopping 100MBs to a mere 1KB.

![](/img/tiny_profile.png)

Using `tiny_profile` is straightforward. Just specify it decorator:

```python
@browser(profile='my-profile',tiny_profile=True,)
def create_accounts(driver: AntiDetectDriver, account):
```

## 📈 Scaling Bots: From One to Many

While setting up an individual bot profile is simple, the real challenge arises when hundreds of such profiles are needed. 

![](/img/profile-editing.gif)

Manually adjusting each profile in the code isn't a practical option when dealing with large numbers of accounts.

### Streamlined Account Generation with `data` 

To address this scalability issue, we've introduced the `data` argument. This function returns a `list of data items`. 

Here's how it works:

1. For every `data item` in the returned `data list`, a new browser instance is launched.
2. The `data item` serves a dual purpose:
   - It's also passed to the `profile`, `user_agent`, `proxy` function as argument, allowing the new browser's configuration to be tailored to the specific account, such as setting the profile based on the account's username.
   
     ```python
    @browser(
        data = lambda: bt.generate_users(3, country=bt.Country.IN)
        profile= lambda account: account['username'],
        is_tiny_profile= True,
    )
    def create_accounts(driver: AntiDetectDriver, account):     
        ...
     ```    

   - It's also sent to the function as its second argument, providing access to individual account details like the `name` and `email`.

     ```python
    @browser(
        data = lambda: bt.generate_users(3, country=bt.Country.IN)
        profile= lambda account: account['username'],
        is_tiny_profile= True,
    )
    def create_accounts(driver: AntiDetectDriver, account):     
        name = account['name']
        email = account['email']
        ...
     ```

### Storing Profile Details for Future Use

Botasaurus introduces a `Profile` Module specifically designed for easy account management. With this module, you can easily:

- Save important account details such as name, email, and password or any other key-value metadata like `api_key` related to the current profile.
- List and remove profiles as needed.

![](/img/profile.png)

When an account is successfully created, it's essential to store its details using the Profile Module. This ensures that the information is available for profile management tasks like listing them.

To store the account details after creation, you can use the `bt.Profile.set_profile` method as follows:

```python
def create_accounts(driver: AntiDetectDriver, account):     
    ...  # Code to Sign Up 
    bt.Profile.set_profile(account)
```

## 🎯 Using Profiles for Actions

The real fun begins when we start using profiles to execute actions.

### The Power of Accounts

After creating multiple accounts on a platform, it's common for each account to execute specific actions. This might include:

- Using the credits provided by the website's free plan (a popular approach).
    - Example: Using the Free Plan of MailChimp to send emails.

- Sending messages to people.
    - Example: Messaging people on LinkedIn to promote your awesome product.

In this tutorial, for the sake of simplicity, we'll focus on a simple task: capturing screenshots of the dashboard for each account. 

While this seems basic, it provides a foundation for understanding how profiles can be utilized to execute various actions on the target website.

### Taking Screenshots

This code enables the capture of screenshots for each created account:

```python
from botasaurus import *

@browser(
    data = lambda: bt.Profile.get_profiles()
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def take_screenshots(driver: AntiDetectDriver, account):
    username = account['username']
    driver.get("https://www.omkar.cloud/")
    driver.save_screenshot(username)

if __name__ == "__main__":
    # Execute the task
    launch_tasks(ScreenShotTask)
```

### Code Breakdown:

Now, let's break this code down bit by bit:

```python

def take_screenshots(driver: AntiDetectDriver, account):
```

This code defines a custom task, `take_screenshots`, which will  capture screenshots from the "https://www.omkar.cloud/" webpage for each profile.

--- 

```python
@browser(
    data = lambda: bt.Profile.get_profiles(),
    ...)
```

Above Code, return all the Accounts. For each Account is the list returned by the `data` function:
    - a new browser will launched
    - will be passed to `profile` for browser configuration and to the wrapped function.

--- 

```python
@browser(
    profile= lambda account: account['username'],
    ...)
```

In above code, we define `get_browser_config()` which determines the profile path to use based on Account Username. 

--- 

```python
def take_screenshots(driver: AntiDetectDriver, account):
    username = account['username']
    driver.get("https://www.omkar.cloud/")
    driver.save_screenshot(username)
```

The function performs the scraping task by visiting to the Omkar Cloud site, capturing a screenshot, and saving it with the username as the filename.

--- 

```python
if __name__ == "__main__":
    take_screenshots()
```
Finally, we launch the task calling the `take_screenshots` function.

--- 

## 🚫 Speed up by Blocking Images

Loading image resources can have a couple of significant downsides like:

- Being heavy on the wallet, especially if you're using residential proxies, which can be very expensive, costing around $15/GB.
- Wasting your time by slowing down the scraping process due to image loading.

### The Solution with Botasaurus

By blocking images from loading, we can achieve faster scraping and also a healthier wallet.

To configure the browser to block images, use the following code, setting the `block_images` parameter to `True`:

```python
@browser(
    block_images=True, # <-
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def take_screenshots(driver: AntiDetectDriver, account):
```

## 🚀 Launch It

Finally, it's time to put all the pieces together. Follow these steps to create 3 accounts on Omkar Cloud and capture their dashboard screenshots:

![](/img/sign-up-bot-running.gif)

1. Create a Python script named `main.py` and paste the following code into `main.py`:

```python
from botasaurus import *

@browser(
    data = lambda: bt.generate_users(3, country=bt.Country.IN)
    block_images=True,
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def create_accounts(driver: AntiDetectDriver, account):
    name = account['name']
    email = account['email']
    password = account['password']

    def sign_up():
        driver.type('input[name="name"]', name)
        driver.type('input[type="email"]', email)
        driver.type('input[type="password"]', password)
        driver.click('button[type="submit"]')

    def confirm_email():
        link = bt.TempMail.get_email_link_and_delete_mailbox(email)
        driver.get(link)

    driver.organic_get("https://www.omkar.cloud/auth/sign-up/")
    sign_up()
    confirm_email()
    bt.Profile.set_profile(account)    

@browser(
    data = lambda: bt.Profile.get_profiles()
    block_images=True,
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def take_screenshots(driver: AntiDetectDriver, account):
    username = account['username']
    driver.get("https://www.omkar.cloud/")
    driver.save_screenshot(username)

if __name__ == "__main__":
    create_accounts()
    take_screenshots()

```

2. Now, run the following command to see multiple accounts being created and screenshots taken:

```sh
python main.py
``` 

## 🔎 Inspecting the Output

After execution, you'll encounter various files and folders providing information about the tasks executed by the bot. Here's a breakdown:

### The `tasks` Folder

This folder contains metadata related to each bot run.

- **`task_info.json`**: This file provides information such as the duration of the task, the IP, the user agent, and the profile associated with the task.
  
  ![Task Info](/img/task-info.png)

- **`final.png`**: This is a screenshot captured just before the driver was closed.
  
  ![Final Screenshot](/img/task-info.png) 

- **`page.html`**: This is the HTML source captured before the driver was closed. This can be especially helpful if your selectors fail to locate the intended elements on the page.
  
  ![Page Source](/img/page.png)

- **`error.log`**: If any errors occur during the bot's operations, they will be logged here.
  
  ![Error Log](/img/error-log.png)

### The `profiles` Folder

In this folder, you'll find `profile.json` for the three accounts that were created. Each `profile.json` file contains cookies specific to that account.

![](/img/cookies.png)

### Screenshots from the Last Three Tasks

Screenshots of each user's dashboard will be captured and placed in the respective task folder.

![](/img/omkar-dashboard.png)

---

After inspecting the output, I encourage you to read the final code provided below to grasp the underlying logic and understand how the pieces fit together.

```python
from botasaurus import *

@browser(
    data = lambda: bt.generate_users(3, country=bt.Country.IN)
    block_images=True,
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def create_accounts(driver: AntiDetectDriver, account):
    name = account['name']
    email = account['email']
    password = account['password']

    def sign_up():
        driver.type('input[name="name"]', name)
        driver.type('input[type="email"]', email)
        driver.type('input[type="password"]', password)
        driver.click('button[type="submit"]')

    def confirm_email():
        link = bt.TempMail.get_email_link_and_delete_mailbox(email)
        driver.get(link)

    driver.organic_get("https://www.omkar.cloud/auth/sign-up/")
    sign_up()
    confirm_email()
    bt.Profile.set_profile(account)    

@browser(
    data = lambda: bt.Profile.get_profiles()
    block_images=True,
    profile= lambda account: account['username'],
    is_tiny_profile= True,
)
def take_screenshots(driver: AntiDetectDriver, account):
    username = account['username']
    driver.get("https://www.omkar.cloud/")
    driver.save_screenshot(username)

if __name__ == "__main__":
    create_accounts()
    take_screenshots()
```

## 🎉 What's Next?

Congratulations, friend, on reaching the end of the tutorial. By now, you have mastered the basics of working with Botasaurus!

Next, we'll enhance your web scraping toolbox by diving into an interesting project: *Scraping Google Maps for Lead Generation*.

![Google Maps Scraper Running](/img/google-maps-scraper-running.gif)

By scraping Google Maps, we can access phone numbers and websites of businesses. This invaluable data allows us to reach out and promote our products effectively.

In this tutorial, not only will you develop a practical scraping tool, but you will also gain hands-on experience in:
- Running bots in parallel for faster scraping.
- Understanding the overall process of a web scraping project with Botasaurus.
- Saving the extracted data in both CSV and JSON formats.
- Setting up your scraper in a Docker environment for consistent and reproducible execution.

Once you complete this tutorial, you'll have achieved mastery over Botasaurus. Dive into the tutorial [here](google-maps-scraping-tutorial.md).