<p align="center">
  <img src="https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/mascot.png" alt="botasaurus" />
</p>
  <div align="center" style="margin-top: 0;">
  <h1>✨ Botasaurus Framework 🤖</h1>
  <p>🚀 Swiss Army Knife for Bot Development 🤖</p>
</div>
<em>
  <h5 align="center">(Programming Language - Python 3)</h5>
</em>
<p align="center">
  <a href="#">
    <img alt="botasaurus forks" src="https://img.shields.io/github/forks/omkarcloud/botasaurus?style=for-the-badge" />
  </a>
  <a href="#">
    <img alt="Repo stars" src="https://img.shields.io/github/stars/omkarcloud/botasaurus?style=for-the-badge&color=yellow" />
  </a>
  <a href="#">
    <img alt="botasaurus License" src="https://img.shields.io/github/license/omkarcloud/botasaurus?color=orange&style=for-the-badge" />
  </a>
  <a href="https://github.com/omkarcloud/botasaurus/issues">
    <img alt="issues" src="https://img.shields.io/github/issues/omkarcloud/botasaurus?color=purple&style=for-the-badge" />
  </a>
</p>
<p align="center">
  <img src="https://views.whatilearened.today/views/github/omkarcloud/botasaurus.svg" width="80px" height="28px" alt="View" />
</p>

# Botasaurus - Your Ultimate Selenium-Based Bot Development Framework

🤖 Hi, I'm Botasaurus, a Selenium-based bot development framework designed to help you become a 10x Bot Developer!

🔍 **What is Botasaurus and How Can it Help Me Become a 10x Bot Developer?**

Think of Botasaurus as a supercharged version of Selenium. If you know Selenium, you're off to a great start because Botasaurus is a framework for Selenium with goodies like:

**1. Account Generation**
   
   - My Account Generation Module enables you to create humane user accounts effortlessly. This is particularly handy when you need multiple accounts while evading detection.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/generated-account.png)

**2. Temporary Email**
   
   - Need to verify those accounts? I've got you covered with an inbuilt Temporary Email Module.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/signup-email.png)

**3. Simple Configuration**
   
   - Configuring profiles, user agents, and proxies can be a headache in Selenium. But with Botasaurus, it's as easy as pie!
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/profile-config.png)

**4. Parallel Bots**
   
   - Run multiple bots in parallel and turn hours of automation into mere minutes with Botasaurus.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/parallel-bots.png)

**5. Easy Debugging**
   
   - Debugging made painless! When a crash occurs due to an incorrect selector, etc., Botasaurus pauses the browser instead of closing it, facilitating on-the-spot debugging.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/error-prompt.png)

   - Capture important details like screenshots, page HTML, error logs, and execution time for easy debugging and generating time estimates of how long to keep the Bot Running.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/debugging.png)

**6. Run Bots at Google's Scale with Kubernetes**
   
   - Seamlessly integrate Botasaurus with Kubernetes to run your bots at Google's Scale. Easily control the number of bots and when to launch them via a simple UI interface.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/kubernetes-integration.webp)

**7. Turbocharge Your Web Scraping**

   - Say goodbye to redundant requests with our powerful caching feature. Botasaurus allows you to cache web scraping results, ensuring lightning-fast performance on subsequent scrapes.

   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/cache.jpg)

**8. Supercharged Selenium Driver**
   
   - Elevate your Selenium game with Botasaurus. We've added Anti-Bot Detection features and added shortcut methods for common operations, all designed to save your valuable time.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/type-click-text.png)

**9. Persist 1000 Profiles in 1 MB**
   
   - Forget about heavy 100 MBs Chrome profiles. Use the Tiny Profile feature to save cookies in just a few KBs.
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/chrome-profile-vs-tiny-profile.png)


**10. Evade IP Suspensions like Ninja Hatori**
   
   - Using a single IP to create accounts and getting suspended?
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/linkedin-restricted.png)
   
   No problem! Ditch expensive $15/GB Residential Proxies and use the FreeProxy Module to connect to the Tor Network and access a vast pool of unique Tor IPs all for free. 
   
   ![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/tor-project-logo-onions.png)

So, if you're comfortable with Selenium and want to level up your bot development game with easy debugging, simple configuration, parallel execution, and temporary emails, then you're in for a treat. Botasaurus is like Selenium on steroids, and you'll love building Bots with it!

So, if you're comfortable with Selenium and want to level up your bot development game with easy debugging, simple configuration, parallel execution, and temporary emails, then you're in for a treat. Botasaurus is like Selenium on steroids, and you'll love building Bots with it!


## 🚀 Getting Started with Botasaurus


Let's quickly grasp how Botasaurus works with a simple example.

In this simple example, we'll walk through the process of scraping the heading text from [https://www.omkar.cloud/](https://www.omkar.cloud/).

![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

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

![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

## 🚀 Deep Dive into Botasaurus

Power of Bots is Immense, A Bot
   - Can apply on your behalf to Linkedin Jobs 24 Hours
   - Scrape Phone Number of Thousands of Buisnesses from Google Maps to sell your Products to.
   - Mass Message People on Twitter/LinkedIn/Reddit for selling your Product
   - Sign Up 100's of Accounts on MailChimp to send 50,000 (500 emails * 100) Emails all for free


So, Ready to unlock the power of Bots? 

📚 **Read the Tutorial** [here](https://www.omkar.cloud/botasaurus/docs/sign-up-tutorial/) and embark on your journey of bot mastery! 🚀

## Love It? Star It! ⭐
