---
sidebar_position: 20
---

# FAQs [Must Read]

## Is it legal to scrape websites?
Web scraping is perfectly legal if you are scraping publicly available data.

## How to solve captchas?

There are two popular methods for solving captchas:

**1. Self Solving:**

If you only have a small number of captchas to solve, typically less than 100, then solving them by yourself is a good option. 

Solving captchas by yourself is free, does not require any code integration, can be done within an hour for less than 100 captchas, and is generally more reliable than captcha solving services. 

I have personally used this method most of the time when creating Outlook or LinkedIn accounts.

To solve captchas by yourself, follow these steps:
1. Add the following code to the bot at the point when the captcha is displayed:
```python
   driver.prompt()
```
2. Solve the captcha by yourself.
3. Press enter to continue with the automation.

**2. Captcha Solving Services:**

If you need to solve a larger number of captchas, say more than 1000, automation becomes necessary. 

In these cases, you can use captcha solving services like 2Captcha, Anti-Captcha, or DeathByCaptcha.

These services offer reasonable prices. For example, the cost of solving 1000 Google reCaptcha using 2Captcha ranges from $1 to $3.

To learn how to solve captchas using 2Captcha, you can read [this article](https://www.omkar.cloud/blog/how-to-solve-captcha-in-selenium-using-2captcha/).

## What are some Bot Detection Services?
Cloudflare, PerimeterX, and DataDome are popular bot detection services that you may encounter while automating websites.

## What are the Best Practices when automating sites that are protected by Bot Detection Services?

To avoid bot detection while automating websites protected by bot detection services, it is recommended to follow these best practices:

1. Use IPs with high reputation. Avoid using data center IPs and opt for home IPs, mobile IPs, or residential proxy IPs, as they are less likely to be blocked.

2. Use Undetected Driver by specifying it in BrowserConfig 
```python
from bose import BaseTask, BrowserConfig

class Task(BaseTask):
    browser_config = BrowserConfig(use_undetected_driver=True)
```

3. Make the bot look humane by adding random waits using methods like `driver.short_random_sleep` and `driver.long_random_sleep`.

4. If your bot gets detected and your IP is blocked, follow these steps to bypass the IP block:

    - Close the browser.
    - Change your IP by using a method like the "Mobile Aeroplane Method" as described in the ["Changing IP" lesson](../change-ip/#methods-for-changing-ip).
    - If you are using a profile, then if possible, delete the stored profile in the profiles folder to remove cookies and local storage set by bot blocking services.
    - Now, rerun the bot. 

    ![Fiverr IP Block](/img/fiverr-block.webp)

## What are the Best Practices when creating a lot of bot accounts on a website?

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

Also, use this template for a great starting point when creating multiple accounts on a website. The template is available [here](../../templates/multiple-account-generation-template/). 


## What will the Target Website do if they recognize an Account created by Bot? 

When a website recognizes an account created by a bot, it can take various actions. Commonly, the bot account is restricted, which can involve limited functionality, posting restrictions, or suspension. 

Here are the Common Actions Taken by Popular Websites

LinkedIn restricts bot accounts:

![LinkedIn Restricted Account](/img/linkedin-restricted.png)

Reddit restricts accounts and disables posting and messaging but allows reading:

![Reddit Restricted Account](/img/reddit-restricted.png)

Fiverr also suspends accounts by sending an email. 

While legal action is possible, it is really rare.
      

## Best Practices for Web Scraping?

Here are some best practices for web scraping:

1. Instead of individually visiting each page to gather links, it is advisable to search for pagination links within sitemaps or RSS feeds. In most cases, these sources provide all links in an organized manner.

![sitemap](/img/sitemap.png)

2. Make the bot look humane by adding random waits using methods like `driver.short_random_sleep` and `driver.long_random_sleep`.

3. If you need to scrape a large amount of data in a short time, consider using proxies to prevent IP-based blocking.

4. If you are responsible for maintaining the scraper in the long run, it is recommended to avoid using hash-based selectors. These selectors will break with the next build of the website, resulting in increased maintenance work.

Note that most websites do not implement bot protection as many frontend developers are not taught bot protection in their courses. 

So, it is recommended to only add IP rotation or random waits if you are getting blocked.

Also, use this template for a great starting point when creating multiple accounts on a website. The template is available [here](../../templates/web-scraping-template/). 

## What are some popular proxy services you can suggest?

Some popular proxy services are Oxylabs, IPRoyal, and BrightData.

I have used BrightData and IPRoyal, and their service was satisfactory. "