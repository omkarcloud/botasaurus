---
sidebar_position: 1
description: Botasaurus is a Swiss Army knife 🔪 for web scraping and browser automation 🤖 that helps you create bots fast. ⚡️
---
# What is Botasaurus?

## In a nutshell

Botasaurus is an all in 1 web scraping framework built for the modern web. We
address the key pain points web scrapers face when scraping the web.

Our aim it to make web scraping extremely easy and save you hours of Development Time.

## Features

Botasaurus comes fully baked, with batteries included. Here is a list of things it can do that no other web scraping framework can:

- **Anti Detect:** Make Anti Detect Requests and Selenium Visits.
- **Debuggability:** When a crash occurs due to an incorrect selector, etc., Botasaurus pauses the browser instead of closing it, facilitating painless on-the-spot debugging.
- **Caching:** Botasaurus allows you to cache web scraping results, ensuring lightning-fast performance on subsequent scrapes.
- **Easy Configuration:** Easily save time with parallelization, profile, and proxy configuration.
- **Time-Saving Selenium Shortcuts:** Botasaurus comes with numerous Selenium shortcuts to make web scraping incredibly easy.

## 🚀 Getting Started with Botasaurus

Welcome to Botasaurus! Let’s dive right in with a straightforward example to understand how it works.

In this tutorial, we will go through the steps to scrape the heading text from [https://www.omkar.cloud/](https://www.omkar.cloud/).

![Botasaurus in action](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

### Step 1: Install Botasaurus

First things first, you need to install Botasaurus. Run the following command in your terminal:

```shell
python -m pip install botasaurus
```

### Step 2: Set Up Your Botasaurus Project

Next, let’s set up the project:

1. Create a directory for your Botasaurus project and navigate into it:

```shell
mkdir my-botasaurus-project
cd my-botasaurus-project
code .  # This will open the project in VSCode if you have it installed
```

### Step 3: Write the Scraping Code

Now, create a Python script named `main.py` in your project directory and insert the following code:

```python
from botasaurus import *

@browser
def scrape_heading_task(driver: AntiDetectDriver, data):
    # Navigate to the Omkar Cloud website
    driver.get("https://www.omkar.cloud/")
    
    # Retrieve the heading element's text
    heading = driver.text("h1")

    # Save the data as a JSON file in output/all.json
    return {
        "heading": heading
    }
     
if __name__ == "__main__":
    # Initiate the web scraping task
    scrape_heading_task()
```

Let’s dissect this code:

- We define a custom scraping task, `scrape_heading_task`, decorated with `@browser`:
```python
@browser
def scrape_heading_task(driver: AntiDetectDriver, data):
```  

- Botasaurus automatically provides an Anti Detection Selenium driver to our function:
```python
def scrape_heading_task(driver: AntiDetectDriver, data):
```  

- Inside the function, we:
    - Navigate to Omkar Cloud
    - Extract the heading text
    - Prepare the data to be automatically saved as JSON and CSV files by Botasaurus:
```python
    driver.get("https://www.omkar.cloud/")
    heading = driver.text("h1")
    return {"heading": heading}
```  

- Finally, we initiate the scraping task:
```python
if __name__ == "__main__":
    scrape_heading_task()
```  

### Step 4: Run the Scraping Task

Time to run your bot:

```shell
python main.py
```

After executing the script, it will:
- Launch Google Chrome
- Navigate to [omkar.cloud](https://www.omkar.cloud/)
- Extract the heading text
- Save it automatically as `output/finished.json`.

![Botasaurus in action](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

Now, let’s explore another way to scrape the heading using the `requests` module. Replace the previous code in `main.py` with the following:

```python
from botasaurus import *

@requests
def scrape_heading_task(requests: AntiDetectRequests, data):
    # Navigate to the Omkar Cloud website
    soup = requests.bs4("https://www.omkar.cloud/")
    
    # Retrieve the heading element's text
    heading = soup.find('h1').get_text()

    # Save the data as a JSON file in output/all.json
    return {
        "heading": heading
    }
     
if __name__ == "__main__":
    # Initiate the web scraping task
    scrape_heading_task()
```

In this code:

- We are using the BeautifulSoup (bs4) module to parse and scrape the heading.
- The `requests` object provided is not a standard Python requests object but an Anti Detect requests object, which also preserves cookies.

### Step 5: Run the Scraping Task (Using Anti Detect Requests)

Finally, run the bot again:

```shell
python main.py
```

This time, you will observe the same result as before, but instead of using Anti Detect Selenium, we are utilizing the Anti Detect requests module.

## 💡 Understanding Botasaurus

Power of Bots is Immense, A Bot
   - Can apply on your behalf to Linkedin Jobs 24 Hours
   - Scrape Phone Number of Thousands of Buisnesses from Google Maps to sell your Products to.
   - Mass Message People on Twitter/LinkedIn/Reddit for selling your Product
   - Sign Up 100's of Accounts on MailChimp to send 50,000 (500 emails * 100) Emails all for free

Let's learn feautres of Botasaurus that helps you unlock these super powers? 

### How to Scrape Multiple Data Points/Links?

To scrape multiple data points or links, define the `data` variable and provide a list of items to be scraped:

```python
@browser(data=["https://www.omkar.cloud/", "https://www.omkar.cloud/blog/", "https://stackoverflow.com/"])
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

Botasaurus will launch a new browser instance for each item in the list and merge the results into a single file at the end of the scraping task (all.csv/all.json).


![TODO:all.csv/all.json Side by Side](/img/.png)

Please note that the `data` parameter can also handle items such as dictionaries.

For instance, if you're automating the sign-up process for bot accounts on a website, you can pass dictionaries to it like so:

```python
@browser(data=[{"name": "Mahendra Singh Dhoni", ...}, {"name": "Virender Sehwag", ...}])
def scrape_heading_task(driver: AntiDetectDriver, data):
    # ...
```

In this example, the `data` parameter is supplied with a lambda function that returns a list of dictionaries. Each dictionary contains details for a different bot account that you wish to sign up.

### How to Scrape in Parallel?

To scrape data in parallel, set the `parallel` option in the browser decorator:

```python
@browser(parallel=3, data=["https://www.omkar.cloud/", ...])
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

### How to know how many scrapers to run parallely?

To determine the optimal number of parallel scrapers, pass the `bt.calc_max_parallel_browsers` function, which calculates the maximum number of browsers that can be run in parallel based on the available RAM:

```python
@browser(parallel=bt.calc_max_parallel_browsers, data=["https://www.omkar.cloud/", ...])
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

*Example: If you have 5.8 GB of free RAM, `bt.calc_max_parallel_browsers` would return 10, indicating you can run up to 10 browsers in parallel.*

### How to Cache the Web Scraping Results?

To cache web scraping results and avoid re-scraping the same data, set `cache=True` in the decorator:

```python
@browser(cache=True, data=["https://www.omkar.cloud/", ...])
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...  
```

### How Botasaurus helps me in debugging?

Botasaurus enhances the debugging experience by pausing the browser instead of closing it when an error occurs. This allows you to inspect the page and understand what went wrong, which can be especially helpful in debugging and removing the hassle of reproducing edge cases.

Botasaurus also plays a beep sound to alert you when an error occurs.

![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/error-prompt.png)

### How to Block Images?

Blocking images can significantly speed up your web scraping tasks. For example, a page that originally takes 4 seconds to load might only take one second to load after images have been blocked.

To block images, simply set `block_images=True` in the decorator:

```python
@browser(block_images=True)
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

### How to Configure UserAgent, Proxy, Chrome Profile, Headless, etc.?

To configure various settings such as UserAgent, Proxy, Chrome Profile, and headless mode, you can specify them in the decorator as shown below:

```python
@browser(
  headless=True, 
  profile='my-profile', 
  proxy="http://your_proxy_address:your_proxy_port",
  user_agent=bt.UserAgents.user_agent_106
)
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

### How Can I Save Data With a Different Name Instead of 'all.json'?

To save the data with a different filename, pass the desired filename along with the data in a tuple as shown below:

```python
@browser(block_images=True, cache=True)
def scrape_article_links(driver: AntiDetectDriver, data):
    # Visit the Omkar Cloud website
    driver.get("https://www.omkar.cloud/blog/")
    
    links = driver.links("h3 a")

    filename = "links"
    return filename, links
```

### I want to Scrape a large number of Links, a new selenium driver is getting created for each new link, this increases the time to scrape data. How can I reuse Drivers?

Utilize the `reuse_drivers` option to reuse drivers, reducing the time required for data scraping:

```python
@browser(reuse_drivers=True)
def scrape_heading_task(driver: AntiDetectDriver, data):
  # ...
```

### Could you show me a practical example where all these Botasaurus Features Come Together to accomplish a typical web scraping project?

Below is a practical example of how Botasaurus features come together in a typical web scraping project to scrape a list of links from a blog, and then visit each link to retrieve the article's heading and date:

```python
@browser(block_images=True,
         cache=True, 
         parallel=bt.calc_max_parallel_browsers, 
         reuse_drivers=True)
def scrape_articles(driver: AntiDetectDriver, link):
    driver.get(link)

    heading = driver.text("h1")
    date = driver.text("time")

    return {
        "heading": heading, 
        "date": date, 
        "link": link, 
    }

@browser(block_images=True, cache=True)
def scrape_article_links(driver: AntiDetectDriver, data):
    # Visit the Omkar Cloud website
    driver.get("https://www.omkar.cloud/blog/")
    
    links = driver.links("h3 a")

    filename = "links"
    return filename, links

if __name__ == "__main__":
    # Launch the web scraping task
    links = scrape_article_links()
    scrape_articles(links)
```


### How to Read/Write JSON and CSV Files?

Botasaurus provides convenient methods for reading and writing data:

```python
# Data to write to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "data.json"
bt.write_json(data, "data.json")

# Read the contents of the file "data.json"
data = bt.read_json("data.json")

# Write the data to the file "data.csv"
bt.write_csv(data, "data.csv")

# Read the contents of the file "data.csv"
bt.read_csv("data.csv")
```

### How Can I Pause the Scraper to Inspect Things While Developing?

To pause the scraper and wait for user input before proceeding, use `driver.prompt()`:

```python
driver.prompt()
```

### How Does AntiDetectDriver Facilitate Easier Web Scraping?

AntiDetectDriver is a patched Version of Selenium that has been modified to avoid detection by bot protection services such as Cloudflare. 

It also includes a variety of helper functions that make web scraping tasks easier.

You can learn about these methods [here](https://github.com/omkarcloud/botasaurus/blob/master/anti-detect-driver.md).

### What Features Does @requests Support, Similar to @browser?

Similar to @browser, @requests supports features like 
 - asynchronous execution [Will Learn Later]
 - parallel processing
 - caching
 - user-agent customization
 - proxies, etc.

Below is an example that showcases these features:


```python
@requests(parallel=40, cache=True, proxy="http://your_proxy_address:your_proxy_port", data=["https://www.omkar.cloud/", ...])
def scrape_heading_task(requests: AntiDetectDriver, link):
  soup = requests.bs4(link)
  heading = soup.find('h1').get_text()
  return {"heading": heading}
```

### I have an existing project into which I want to integrate the AntiDetectDriver/AntiDetectRequests.

You can create an instance of `AntiDetectDriver` as follows:
```python
driver = bt.create_driver()
# ... Code for scraping
driver.quit()
```

You can create an instance of `AntiDetectRequests` as follows:
```python
anti_detect_requests = bt.create_requests()
soup = anti_detect_requests.bs4("https://www.omkar.cloud/")
# ... Additional code
```

--- 

*Sign Up Bots*
Sometimes, when scraping the web, data is hidden behind an authentication wall, requiring you to sign up via email or Google to access it.

Now, let's explore how to use Botasaurus utilities that empower us to create hundreds of accounts on a website. With hundreds of bots at your command:

  - You can mass message thousands of people on platforms like Twitter, LinkedIn, or Reddit to promote your product.

  - Platforms like MailChimp offer free plans with limited usage. With bots, you can maximize the benefits of these plans. For instance, if MailChimp allows you to send 500 emails per month for free, with 100 bots, you can send 50,000 emails monthly.

---

### How to Generate Human-Like User Data?

To create human-like user data, use the `generate_user` function:

```python
user = bt.generate_user(country=bt.Country.IN)
```

This will generate user profiles similar to the one shown below:

![Account](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/generated-account.png)

The data generated is very realistic, reducing the likelihood of being flagged as a bot.

### The Target Website Has Sent a Verification Email: How to Get the Link and Verify It?

To get the verification link from an email and then delete the mailbox, use `bt.TempMail.get_email_link_and_delete_mailbox` as shown below:

```python
user = bt.generate_user(country=bt.Country.IN)
email = user["email"]  # Example: madhumitachavare@1974.icznn.com

link = bt.TempMail.get_email_link_and_delete_mailbox(email)  # Retrieves the Verification Link and Deletes the Mailbox

driver.get(link)
```

### I have automated the Creation of User Account's. Now I want to store the User Account Credentials like Email and Password. How to store it?

To store user-related data, such as account credentials, use the `ProfileManager` module:

```python
bt.Profile.set_profile(user)
```

In cases where you want to store metadata related to a user, such as API keys:

```python
bt.Profile.set_item("api_key", "BDEC26...")
```

To retrieve a list of all users, use `bt.Profile.get_all_profiles()`:

```python
profiles = bt.Profile.get_all_profiles()
```

### The Chrome Profiles of User's are getting very large like 100MBs, is there a way to Compress them? 

You can use tiny_profile feautre of Botasaurus which are a replacement for Chrome Profiles.

Each Tiny Profile only stores cookies from visited websites, making them extremely lightweight—around 1KB. Here's how to use them:

```python
@browser(
    tiny_profile=True, 
    profile='my-profile',
)
def sign_up_task(driver: AntiDetectDriver, data):
    # Your sign-up code here
```

### How to Dynamically Specify the Profile Based on a Data Item?

You can dynamically select a profile by passing a function to the `profile` option, which will receive the data item:

```python
@browser(
    data=[{"username": "mahendra-singh-dhoni", ...}, {"username": "virender-sehwag", ...}],
    profile=lambda data: data["username"],
)
def sign_up_task(driver: AntiDetectDriver, data):
    # Your sign-up code here
```

user_agent, proxy, and other options can also be passed functions.

### Is there a Tutorial that integrates tiny_profile, temp mail, user generator, profile to sign up on a Website and Perform Actions on Website. So I can get a Complete Picture?

For a comprehensive guide on using Botasaurus features such as `tiny_profile`, `temp_mail`, `user_generator`, and `profile` to sign up on a website and perform actions, read the Sign-Up Tutorial [Here](https://www.omkar.cloud/botasaurus/docs/sign-up-tutorial/). 

This tutorial will walk you through signing up for 3 accounts on Omkar Cloud and give you a complete understanding of the process.

### How to Run Botasaurus in Docker?

To run Botasaurus in Docker, use the Botasaurus Starter Template, which includes the necessary Dockerfile and Docker Compose configurations:

```
git clone https://github.com/omkarcloud/botasaurus-starter my-botasaurus-project
cd my-botasaurus-project
docker-compose build && docker-compose up
```

### How to Run Botasaurus in Gitpod?

Botasaurus Starter Template comes with the necessary `.gitpod.yml` to easily run it in Gitpod, a browser-based development environment. Set it up in just 5 minutes by following these steps:

1. Open Botasaurus Starter Template, by visiting [this link](https://gitpod.io/#https://github.com/omkarcloud/botasaurus-starter) and sign up using your GitHub account.
   
   ![Screenshot (148)](https://github.com/omkarcloud/google-maps-scraper/assets/53407137/f498dda8-5352-4f7a-9d70-c717859670d4.png)
  
2. To speed up scraping, select the Large 8 Core, 16 GB Ram Machine and click the `Continue` button.   

   ![16gb select](https://raw.githubusercontent.com/omkarcloud/google-maps-scraper/master/screenshots/16gb-select.png)

3. In the terminal, run the following command to start scraping:
   ```bash
   python main.py
   ```

Please understand:
   - The internet speed in Gitpod is extremely fast at around 180 Mbps.

      ![speedtest](https://raw.githubusercontent.com/omkarcloud/google-maps-scraper/master/screenshots/speedtest.png)

   - When Scraping, You need to interact with Gitpod, such as clicking within the environment, every 30 minutes to prevent the machine from automatically closing.


*Advanced Features*

### How to Run Drivers Asynchronously from the Main Process?

To execute drivers asynchronously, enable the `async` option and use `.get()` when you're ready to collect the results:

```python
from time import sleep

@browser(
    async=True,  # Specify the Async option here
)
def scrape_heading(driver: AntiDetectDriver, data):
    print("Sleeping for 5 seconds.")
    sleep(5)
    print("Slept for 5 seconds.")
    return {}

if __name__ == "__main__":
    # Launch web scraping tasks asynchronously
    result1 = scrape_heading()  # Launches asynchronously
    result2 = scrape_heading()  # Launches asynchronously

    result1.get()  # Wait for the first result
    result2.get()  # Wait for the second result
```

With this method, function calls run concurrently. The output will indicate that both function calls are executing in parallel.

### I want to repeatedly call the scraping function without creating new Selenium drivers each time. How can I achieve this?

Utilize the `keep_drivers_alive` option to maintain active driver sessions. Remember to call `.done()` when you're finished to release resources:

```python
@browser(
    keep_drivers_alive=True, 
    parallel=bt.calc_max_parallel_browsers,  # Typically used with `keep_drivers_alive`
    reuse_drivers=True,  # Also commonly paired with `keep_drivers_alive`
)
def scrape_data(driver: AntiDetectDriver, data):
    # ... (Your scraping logic here)

if __name__ == "__main__":
    for i in range(3):
        scrape_data()
    # After completing all scraping tasks, call .done() to close the drivers.
    scrape_data.done()
```

---

### Conclusion

Botasaurus is a powerful, flexible tool for web scraping. 

Its various settings allow you to tailor the scraping process to your specific needs, improving both efficiency and convenience. Whether you're dealing with multiple data points, requiring parallel processing, or need to cache results, Botasaurus provides the features to streamline your scraping tasks.

## 🚀 Deep Dive into Botasaurus

📚 **Read the Sign Up Tutorial** [here](sign-up-tutorial.md) to learn the knowledge to create 100's of Accounts on a Website! 🚀