<p align="center">
  <img src="https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/mascot.png" alt="botasaurus" />
</p>
  <div align="center" style="margin-top: 0;">
  <h1>🤖 Botasaurus 🤖</h1>
  </div>

<h3 align="center">
  The All in One Framework to Build Undefeatable Scrapers
</h3>

<p align="center">
  <b>The web has evolved. Finally, web scraping has too.</b>
</p>


<p align="center">
  <img src="https://views.whatilearened.today/views/github/omkarcloud/botasaurus.svg" width="80px" height="28px" alt="View" />
</p>


<p align="center">
  <a href="https://gitpod.io/#https://github.com/omkarcloud/botasaurus-starter">
    <img alt="Run in Gitpod" src="https://gitpod.io/button/open-in-gitpod.svg" />
  </a>
</p>

## 🐿️ Botasaurus In a Nutshell

How wonderful that of all the web scraping tools out there, you chose to learn about Botasaurus. Congratulations! 

And now that you are here, you are in for an exciting, unusual, and rewarding journey that will make your web scraping life a lot easier.

Now, let me tell you about Botasaurus in bullet points. (Because as per marketing gurus, YOU as a member of the Developer Tribe have a VERY short attention span.)

*So, what is Botasaurus?*

Botasaurus is an all-in-one web scraping framework that enables you to build awesome scrapers in less time, with less code, and with more fun.

We have put all our web scraping experience and best practices into Botasaurus to save you hundreds of hours of development time! 

Now, for the magical powers awaiting you after learning Botasaurus:

- In terms of humaneness, what Superman is to Man, Botasaurus is to Selenium and Playwright. Easily pass every (Yes, E-V-E-R-Y) bot test, and build undetected scrapers.  
    
In the video below, watch as we **bypass some of the best bot detection systems**:

- ✅ [Cloudflare Web Application Firewall (WAF)](https://nopecha.com/demo/cloudflare)  
- ✅ [BrowserScan Bot Detection](https://www.browserscan.net/bot-detection)  
- ✅ [Fingerprint Bot Detection](https://fingerprint.com/products/bot-detection/)  
- ✅ [Datadome Bot Detection]((https://fingerprint-scan.com/))  
- ✅ [Cloudflare Turnstile CAPTCHA](https://turnstile.zeroclover.io/)

<p align="center">
<video src='https://github.com/user-attachments/assets/b4f6171f-f2a2-4255-9feb-2973ee9a25ae'/>
</p>

🔗 Want to try it yourself?
See the code behind these tests [here](https://github.com/omkarcloud/botasaurus/blob/master/bot_detection_tests.py)

- Perform realistic, human-like mouse movements and say sayonara to detection
![human-mode-demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/human-mode-demo.gif)

- Convert your scraper into a desktop app for Mac, Windows, and Linux in 1 day, so not only developers but everyone can use your web scraper.

![desktop-app-photo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/desktop-app-photo.png)

- Turn your scraper into a beautiful website, making it easy for your customers to use it from anywhere, anytime.

![pro-gmaps-demo](https://raw.githubusercontent.com/omkarcloud/google-maps-scraper/master/screenshots/demo.gif)

- Save up to 97%, yes 97%, on browser proxy costs by using [browser-based fetch requests.](https://github.com/omkarcloud/botasaurus#how-to-significantly-reduce-proxy-costs-when-scraping-at-scale)

- Easily save hours of development time with easy parallelization, profiles, extensions, and proxy configuration. Botasaurus makes asynchronous, parallel scraping child's play.

- Use caching, sitemap, data cleaning, and other utilities to save hours of time spent writing and debugging code.

- Easily scale your scraper to multiple machines with Kubernetes, and get your data faster than ever.

And those are just the highlights. I mean! 

There is so much more to Botasaurus that you will be amazed at how much time you will save with it.

## 🚀 Getting Started with Botasaurus

Let's dive right in with a straightforward example to understand Botasaurus.

In this example, we will go through the steps to scrape the heading text from [https://www.omkar.cloud/](https://www.omkar.cloud/).

![Botasaurus in action](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

### Step 1: Install Botasaurus

First things first, you need to install Botasaurus. Run the following command in your terminal:

```shell
python -m pip install --upgrade botasaurus
```

### Step 2: Set Up Your Botasaurus Project

Next, let's set up the project:

1. Create a directory for your Botasaurus project and navigate into it:

```shell
mkdir my-botasaurus-project
cd my-botasaurus-project
code .  # This will open the project in VSCode if you have it installed
```

### Step 3: Write the Scraping Code

Now, create a Python script named `main.py` in your project directory and paste the following code:

```python
from botasaurus.browser import browser, Driver

@browser
def scrape_heading_task(driver: Driver, data):
    # Visit the Omkar Cloud website
    driver.get("https://www.omkar.cloud/")
    
    # Retrieve the heading element's text
    heading = driver.get_text("h1")

    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        "heading": heading
    }
     
# Initiate the web scraping task
scrape_heading_task()
```

Let's understand this code:

- We define a custom scraping task, `scrape_heading_task`, decorated with `@browser`:
```python
@browser
def scrape_heading_task(driver: Driver, data):
```  

- Botasaurus automatically provides a Humane Driver to our function:
```python
def scrape_heading_task(driver: Driver, data):
```  

- Inside the function, we:
    - Visit Omkar Cloud
    - Extract the heading text
    - Return the data to be automatically saved as `scrape_heading_task.json` by Botasaurus:
```python
    driver.get("https://www.omkar.cloud/")
    heading = driver.get_text("h1")
    return {"heading": heading}
```  

- Finally, we initiate the scraping task:
```python
# Initiate the web scraping task
scrape_heading_task()
```  

### Step 4: Run the Scraping Task

Time to run it:

```shell
python main.py
```

After executing the script, it will:
- Launch Google Chrome
- Visit [omkar.cloud](https://www.omkar.cloud/)
- Extract the heading text
- Save it automatically as `output/scrape_heading_task.json`.

![Botasaurus in action](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-bot-running.gif)

Now, let's explore another way to scrape the heading using the `request` module. Replace the previous code in `main.py` with the following:

```python
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def scrape_heading_task(request: Request, data):
    # Visit the Omkar Cloud website
    response = request.get("https://www.omkar.cloud/")

    # Create a BeautifulSoup object    
    soup = soupify(response)
    
    # Retrieve the heading element's text
    heading = soup.find('h1').get_text()

    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        "heading": heading
    }     
# Initiate the web scraping task
scrape_heading_task()
```

In this code:

- We scrape the HTML using `request`, which is specifically designed for making browser-like humane requests.
- Next, we parse the HTML into a `BeautifulSoup` object using `soupify()` and extract the heading.

### Step 5: Run the Scraping Task (which makes Humane HTTP Requests)

Finally, run it again:

```shell
python main.py
```

This time, you will observe the exact same result as before, but instead of opening a whole browser, we are making browser-like humane HTTP requests.

## 💡 Understanding Botasaurus

### What is Botasaurus Driver, and why should I use it over Selenium and Playwright?

Botasaurus Driver is a web automation driver like Selenium, and the single most important reason to use it is because it is truly humane. You will not, and I repeat NOT, have any issues accessing any website.

Plus, it is super fast to launch and use, and the API is designed by and for web scrapers, and you will love it.

### How do I access Cloudflare-protected pages using Botasaurus?

Cloudflare is the most popular protection system on the web. So, let's see how Botasaurus can help you solve various Cloudflare challenges.

**Connection Challenge**

This is the single most popular challenge and requires making a browser-like connection with appropriate headers. It's commonly used for:
- Product Pages
- Blog Pages 
- Search Result Pages

<!-- Example Page: https://www.g2.com/products/github/reviews -->

#### What Works?

- Visiting the website via Google Referrer (which makes it seem as if the user has arrived from a Google search).

```python
from botasaurus.browser import browser, Driver

@browser
def scrape_heading_task(driver: Driver, data):
    # Visit the website via Google Referrer
    driver.google_get("https://www.cloudflare.com/en-in/")
    driver.prompt()
    heading = driver.get_text('h1')
    return heading

scrape_heading_task()
```

- Use the request module. The Request Object is smart and, by default, visits any link with a Google Referrer. Although it works, you will need to use retries.

```python
from botasaurus.request import request, Request

@request(max_retry=10)
def scrape_heading_task(request: Request, data):
    response = request.get("https://www.cloudflare.com/en-in/")
    print(response.status_code)
    response.raise_for_status()
    return response.text

scrape_heading_task()
```

**JS with Captcha Challenge**

This challenge requires performing JS computations that differentiate a Chrome controlled by Selenium/Puppeteer/Playwright from a real Chrome. It also involves solving a Captcha. It's used to for pages which are rarely but sometimes visited by people, like:
- 5th Review page
- Auth pages

Example Page: https://nopecha.com/demo/cloudflare

#### What Does Not Work?
Using `@request` does not work because although it can make browser-like HTTP requests, it cannot run JavaScript to solve the challenge.

#### What Works?
Pass the `bypass_cloudflare=True` argument to the `google_get` method.

```python
from botasaurus.browser import browser, Driver

@browser
def scrape_heading_task(driver: Driver, data):
    driver.google_get("https://nopecha.com/demo/cloudflare", bypass_cloudflare=True)
    driver.prompt()

scrape_heading_task()
```
![Cloudflare JS with Captcha Challenge Demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/cloudflare-js-captcha-demo.gif)

### What are the benefits of a UI scraper?

Here are some benefits of creating a scraper with a user interface:

- Simplify your scraper usage for customers, eliminating the need to teach them how to modify and run your code.
- Protect your code by hosting the scraper on the web and offering a monthly subscription, rather than providing full access to your code. This approach:
  - Safeguards your Python code from being copied and reused, increasing your customer's lifetime value.
  - Generate monthly recurring revenue via subscription from your customers, surpassing a one-time payment.
- Enable sorting, filtering, and downloading of data in various formats (JSON, Excel, CSV, etc.).
- Provide access via a REST API for seamless integration.
- Create a polished frontend, backend, and API integration with minimal code.

### How to run a UI-based scraper?

Let's run the Botasaurus Starter Template (the recommended template for greenfield Botasaurus projects), which scrapes the heading of the provided link by following these steps:

1. Clone the Starter Template:
   ```
   git clone https://github.com/omkarcloud/botasaurus-starter my-botasaurus-project
   cd my-botasaurus-project
   ```

2. Install dependencies (will take a few minutes):
   ```
   python -m pip install -r requirements.txt
   python run.py install
   ```

3. Run the scraper:
   ```
   python run.py
   ```

Your browser will automatically open up at http://localhost:3000/. Then, enter the link you want to scrape (e.g., https://www.omkar.cloud/) and click on the Run Button.

![starter-scraper-demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-scraper-demo.gif)

After some seconds, the data will be scraped.
![starter-scraper-demo-result](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-scraper-demo-result.png)

Visit http://localhost:3000/output to see all the tasks you have started.

![starter-scraper-demo-tasks](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-scraper-demo-tasks.png)

Go to http://localhost:3000/about to see the rendered README.md file of the project.

![starter-scraper-demo-readme](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-scraper-demo-readme.png)

Finally, visit http://localhost:3000/api-integration to see how to access the scraper via API.

![starter-scraper-demo-api](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-scraper-demo-api.png)

The API documentation is generated dynamically based on your scraper's inputs, sorts, filters, etc., and is unique to your scraper. 

So, whenever you need to run the scraper via API, visit this tab and copy the code specific to your scraper.

### How to create a UI scraper using Botasaurus?

Creating a UI scraper with Botasaurus is a simple 3-step process:
1. Create your scraper function
2. Add the scraper to the server using 1 line of code 
3. Define the input controls for the scraper

To understand these steps, let's go through the code of the Botasaurus Starter Template that you just ran.

#### Step 1: Create the Scraper Function

In `src/scrape_heading_task.py`, we define a scraping function that basically does the following:

1. Receives a `data` object and extracts the "link".
2. Retrieves the HTML content of the webpage using the "link".
3. Converts the HTML into a BeautifulSoup object.
4. Locates the heading element, extracts its text content, and returns it.

```python
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def scrape_heading_task(request: Request, data):
    # Visit the Link
    response = request.get(data["link"])

    # Create a BeautifulSoup object    
    soup = soupify(response)
    
    # Retrieve the heading element's text
    heading = soup.find('h1').get_text()

    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        "heading": heading
    }
```

#### Step 2: Add the Scraper to the Server

In `backend/scrapers.py`, we:
- Import our scraping function
- Use `Server.add_scraper()` to register the scraper

```python
from botasaurus_server.server import Server
from src.scrape_heading_task import scrape_heading_task

# Add the scraper to the server
Server.add_scraper(scrape_heading_task)
```

#### Step 3: Define the Input Controls

In `backend/inputs/scrape_heading_task.js`, we:
- Define a `getInput` function that takes the controls parameter
- Add a link input control to it
- Use JSDoc comments to enable IntelliSense Code Completion in VSCode as you won't be able to remember all the controls in botasaurus.


```js
/**
 * @typedef {import('../../frontend/node_modules/botasaurus-controls/dist/index').Controls} Controls
 */

/**
 * @param {Controls} controls
 */
function getInput(controls) {
    controls
        // Render a Link Input, which is required, defaults to "https://stackoverflow.blog/open-source". 
        .link('link', { isRequired: true, defaultValue: "https://stackoverflow.blog/open-source" })
}
```

Above was a simple example; below is a real-world example with multi-text, number, switch, select, section, and other controls.

```js
/**
 * @typedef {import('../../frontend/node_modules/botasaurus-controls/dist/index').Controls} Controls
 */


/**
 * @param {Controls} controls
 */
function getInput(controls) {
    controls
        .listOfTexts('queries', {
            defaultValue: ["Web Developers in Bangalore"],
            placeholder: "Web Developers in Bangalore",
            label: 'Search Queries',
            isRequired: true
        })
        .section("Email and Social Links Extraction", (section) => {
            section.text('api_key', {
                placeholder: "2e5d346ap4db8mce4fj7fc112s9h26s61e1192b6a526af51n9",
                label: 'Email and Social Links Extraction API Key',
                helpText: 'Enter your API key to extract email addresses and social media links.',
            })
        })
        .section("Reviews Extraction", (section) => {
            section
                .switch('enable_reviews_extraction', {
                    label: "Enable Reviews Extraction"
                })
                .numberGreaterThanOrEqualToZero('max_reviews', {
                    label: 'Max Reviews per Place (Leave empty to extract all reviews)',
                    placeholder: 20,
                    isShown: (data) => data['enable_reviews_extraction'], defaultValue: 20,
                })
                .choose('reviews_sort', {
                    label: "Sort Reviews By",
                    isRequired: true, isShown: (data) => data['enable_reviews_extraction'], defaultValue: 'newest', options: [{ value: 'newest', label: 'Newest' }, { value: 'most_relevant', label: 'Most Relevant' }, { value: 'highest_rating', label: 'Highest Rating' }, { value: 'lowest_rating', label: 'Lowest Rating' }]
                })
        })
        .section("Language and Max Results", (section) => {
            section
                .addLangSelect()
                .numberGreaterThanOrEqualToOne('max_results', {
                    placeholder: 100,
                    label: 'Max Results per Search Query (Leave empty to extract all places)'
                })
        })
        .section("Geo Location", (section) => {
            section
                .text('coordinates', {
                    placeholder: '12.900490, 77.571466'
                })
                .numberGreaterThanOrEqualToOne('zoom_level', {
                    label: 'Zoom Level (1-21)',
                    defaultValue: 14,
                    placeholder: 14
                })
        })
}
```

I encourage you to paste the above code into `backend/inputs/scrape_heading_task.js` and reload the page, and you will see a complex set of input controls like the image shown.

![complex-input](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/complex-input.png)

Now, to use the Botasaurus UI for adding new scrapers, remember these points:

1. Create a `backend/inputs/{your_scraping_function_name}.js` file for each scraping function.
2. Define the `getInput` function in the file with the necessary controls.
3. Use JSDoc comments to enable IntelliSense code completion in VSCode, as you won't be able to remember all the controls in Botasaurus.

Use this template as a starting point for new scraping function's input controls js file:

```js
/**
 * @typedef {import('../../frontend/node_modules/botasaurus-controls/dist/index').Controls} Controls
 */

/**
 * @param {Controls} controls
 */
function getInput(controls) {
    // Define your controls here.
}
```

That's it! With these simple steps, you can create a fully functional UI scraper using Botasaurus.

Later, you will learn how to add sorts and filters to make your UI scraper even more powerful and user-friendly.

![sorts-filters](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/sorts-filters.png)

### What is a Desktop Extractor?
A **Desktop Extractor** is a standalone application that runs on your computer and extracts specific data from websites, PDFs, Excel files, and other documents. Unlike web-based tools, desktop extractors run locally, giving **faster performance** and **zero cloud costs**.

![Desktop Extractor showing an application interface with extraction options](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/desktop-app-photo.png)

### What advantages do Desktop Scrapers have over web-based scrapers?
**Desktop Scrapers** offer key advantages over web-based scraper solutions like Outscraper:  

- **Zero Infrastructure Costs**: 
   - Runs on the user's machine, eliminating expensive cloud computing fees.  
   - Lower cloud costs allow you to offer lower pricing, attracting more customers and increasing revenue.

- **Faster Execution**:  
  - Instant execution, no delays for cloud resource allocation.  
  - Uses the user's system, which is much faster than shared cloud servers.  

- **Increased Customer Engagement**:  
  The app sits right on the user's desktop, encouraging frequent use compared to web tools they must actively visit via browser.  

- **Cross-Platform Deployment in 1 Day**:  
  With **Botasaurus**, you can launch a desktop scraper for **Windows, macOS, and Linux** within a day. No need to build a website, manage servers, or handle scaling issues. Bota Desktop includes built-in features such as:
  - Task management
  - Data Table
  - Data export (Excel, CSV, etc.)
  - Sorting & Filtering
  - Caching and many more

With zero usage costs, faster performance, and easier development, Desktop Scrapers outperform web-based alternatives.

### How to Build a Desktop Extractor
Creating Desktop Extractors is easier than you think! All you need is a basic understanding of JavaScript. Once you're ready, read the [Desktop Extraction Tutorial](https://www.omkar.cloud/botasaurus/docs/botasaurus-desktop/quick-start), where we'll guide you through building two practical extractors:
- **Yahoo Finance Stock Scraper** – Extracts real-time stock prices from Yahoo Finance.

![Stock Scraper Demo showing the application extracting stock prices from Yahoo Finance](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-scraper-preview.gif) 

- **Amazon Invoice PDF Extractor** – Automates the extraction of key invoice data like Document Number, Document Date, and Place of Supply from Amazon PDFs.  

![PDF Extraction Demo showing the application extracting data from Amazon PDF invoices](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/pdf-extract-preview.gif)  

As a web scraper, you might naturally want to focus on web scraping. Still, I want you to create the **Amazon Invoice PDF Extractor** project. Why? Because many developers overlook the immense potential of extracting data from PDFs, Excel files, and other documents.  

**Document Data Extraction is a large untapped market.** For example, even in most developed countries, accountants often spend hundreds of hours manually entering invoice data for tax filings. A desktop extractor can transform this tedious, error-prone process into a task that takes just minutes, delivering 100% accurate results.

Please read the step-by-step tutorial [here](https://www.omkar.cloud/botasaurus/docs/botasaurus-desktop/quick-start). By the end of this short guide, you'll be able to create powerful desktop extractors in very little time.

### What is Botasaurus, and what are its main features?

Botasaurus is an all-in-one web scraping framework designed to achieve three main goals:  

1. Provide essential web scraping utilities to streamline the scraping process.

To accomplish these goals, Botasaurus gives you 3 decorators:
- `@browser`: For scraping web pages using a humane browser.
- `@request`: For scraping web pages using lightweight and humane HTTP requests.
- `@task`: 
  - For scraping web pages using third-party libraries like `playwright` or `selenium`.
  - or, For running non-web scraping tasks, such as data processing (e.g., converting video to audio). Botasaurus is not limited to web scraping tasks; any Python function can be made accessible with a stunning UI and user-friendly API.

In practice, while developing with Botasaurus, you will spend most of your time in the following areas:
- Configuring your scrapers via decorators with settings like:
  - Which proxy to use
  - How many scrapers to run in parallel, etc.
- Writing your core web scraping logic using BeautifulSoup (bs4) or the Botasaurus Driver.

Additionally, you will utilize the following Botasaurus utilities for debugging and development:
- `bt`: Mainly for writing JSON, EXCEL, and HTML temporary files, and for data cleaning.
- `Sitemap`: For accessing the website's links and sitemap.
- Minor utilities like:
  - `LocalStorage`: For storing scraper state.
  - `soupify`: For creating BeautifulSoup objects from Driver, Requests response, Driver Element, or HTML string.
  - `IPUtils`: For obtaining information (IP, country, etc.) about the current IP address.
  - `Cache`: For managing the cache.

By simply configuring these three decorators (`@browser`, `@request`, and `@task`) with arguments, you can easily create `real-time scrapers` and `large-scale datasets`, thus saving you countless hours that would otherwise be spent writing and debugging code from scratch.

2. Offering a Python-based UI scraper that allows non-technical users to run scrapers online by simply visiting a website link. (As described in the previous FAQ)  

3. Make it easy to create desktop applications for Mac, Windows, and Linux, using JavaScript. More details can be found in the [Botasaurus Desktop Documentation here](https://www.omkar.cloud/botasaurus/docs/botasaurus-desktop/introduction).

### How to use decorators in Botasaurus?

Decorators are the heart of Botasaurus. To use a decorator function, you can call it with:
- A single item
- A list of items

If a scraping function is given a list of items, it will sequentially call the scraping function for each data item.

For example, if you pass a list of three links to the `scrape_heading_task` function:
```python
from botasaurus.browser import browser, Driver

@browser
def scrape_heading_task(driver: Driver, link):
    driver.get(link)
    heading = driver.get_text("h1")
    return heading

scrape_heading_task(["https://www.omkar.cloud/", "https://www.omkar.cloud/blog/", "https://stackoverflow.com/"]) # <-- list of items
```

Then, Botasaurus will launch a new browser instance for each item, and the final results will be stored in `output/scrape_heading_task.json`.

![list-demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/list-demo.gif)

### How does Botasaurus help me in debugging?

Botasaurus helps you in debugging by:

- Easily viewing the result of the scraping function, as it is saved in `output/{your_scraping_function_name}.json`. Say goodbye to print statements.

![scraped data](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/scraped-data.png)

- Bringing your attention to errors in browser mode with a beep sound and pausing the browser, allowing you to debug the error on the spot.

![](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/error-prompt.png)

- Even if an exception is raised in headless mode, it will still open the website in your default browser, making it easier to debug code in a headless browser. (Isn't it cool?)

![headless-error](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/headless-error.png)

### How to configure the Browser Decorator?

The Browser Decorator allows you to easily configure various aspects of the browser, such as:

- Blocking images and CSS
- Setting up proxies
- Specifying profiles
- Enabling headless mode
- Using Chrome extensions
- Captcha Solving
- Selecting language
- Passing Arguments to Chrome

#### Blocking Images and CSS

Blocking images is one of the most important configurations when scraping at scale. Blocking images can significantly: 
- Speed up your web scraping tasks
- Reduce bandwidth usage
- And save money on proxies. (Best of All!)

For example, a page that originally takes 4 seconds and 12 MB to load might only take one second and 100 KB after blocking images and CSS.

To block images, use the `block_images` parameter:

```python
@browser(
    block_images=True,
)
```

To block both images and CSS, use `block_images_and_css`:

```python
@browser(
    block_images_and_css=True,
)    
```

#### Proxies

To use proxies, simply specify the `proxy` parameter:

```python
@browser(
    proxy="http://username:password@proxy-provider-domain:port"
)    
def visit_what_is_my_ip(driver: Driver, data):
    driver.get("https://whatismyipaddress.com/")
    driver.prompt()

visit_what_is_my_ip()
```

You can also pass a list of proxies, and the proxy will be automatically rotated:

```python
@browser(
    proxy=[
        "http://username:password@proxy-provider-domain:port", 
        "http://username2:password2@proxy-provider-domain:port"
    ]
)
def visit_what_is_my_ip(driver: Driver, data):
    driver.get("https://whatismyipaddress.com/")
    driver.prompt()

visit_what_is_my_ip() 
```

#### Profile

Easily specify the Chrome profile using the `profile` option:

```python
@browser(
    profile="pikachu"
)    
```

However, each Chrome profile can become very large (e.g., 100 MB) and can eat up all your computer storage. 

To solve this problem, use the `tiny_profile` option, which is a lightweight alternative to Chrome profiles. 

When creating hundreds of Chrome profiles, it is highly recommended to use the `tiny_profile` option because:

- Creating 1000 Chrome profiles will take at least 100 GB, whereas 1000 tiny profiles will take up only 1 MB of storage, making tiny profiles easy to store and back up.
- Tiny profiles are cross-platform, meaning you can create profiles on a Linux server, copy the `./profiles` folder to a Windows PC, and easily run them.

Under the hood, tiny profiles persist cookies from visited websites, making them extremely lightweight (around 1 KB) while providing the same session persistence.

Here's how to use the tiny profile:

```python
@browser(
    tiny_profile=True, 
    profile="pikachu",
)    
```

#### Headless Mode

Enable headless mode with `headless=True`:
```python
@browser(
    headless=True
)    
```
Note that if you use headless mode, you will surely be identified by services like Cloudflare and Datadome. Therefore, use headless mode only when scraping websites that don't use such services.

#### Chrome Extensions

Botasaurus allows the use of ANY Chrome Extension with just 1 line of code. The example below shows how to use the Mouse Coordinates Chrome Extension to show current mouse X and Y coordinates on web pages:

```python
from botasaurus.browser import browser, Driver
from chrome_extension_python import Extension

@browser(
    extensions=[
        Extension(
            "https://chromewebstore.google.com/detail/mouse-coordinates/mfohnjojhopfcahiddmeljeholnciakl"
        )
    ],
)
def scrape_while_blocking_ads(driver: Driver, data):
    driver.get("https://example.com/")
    driver.prompt()

scrape_while_blocking_ads()
```

In some cases, an extension may require additional configuration, such as API keys or credentials. For such scenarios, you can create a custom extension. Learn more about creating and configuring custom extensions [here](https://github.com/omkarcloud/chrome-extension-python).

#### Captcha Solving

Encountering captchas is common in web scraping. You can use the [capsolver_extension_python](https://github.com/omkarcloud/capsolver-extension-python?tab=readme-ov-file#installation) package to automatically solve CAPTCHAs with Capsolver.  

To use it, first install the package:  

```bash
python -m pip install capsolver_extension_python
```

Then, integrate it into your code as follows:  

```python
from botasaurus.browser import browser, Driver
from capsolver_extension_python import Capsolver

# Replace "CAP-MY_KEY" with your actual CapSolver API key
@browser(extensions=[Capsolver(api_key="CAP-MY_KEY")])  
def solve_captcha(driver: Driver, data):
    driver.get("https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php")
    driver.prompt()

solve_captcha()
```  

#### Language

Specify the language using the `lang` option:

```python
from botasaurus.lang import Lang

@browser(
    lang=Lang.Hindi,
)
```

#### User Agent and Window Size

To make the browser really humane, Botasaurus does not change browser fingerprints by default, because using fingerprints makes the browser easily identifiable by running CSS tests to find mismatches between the provided user agent and the actual user agent.

However, if you need fingerprinting, use the `user_agent` and `window_size` options:

```python
from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from botasaurus.window_size import WindowSize

@browser(
    user_agent=UserAgent.RANDOM,
    window_size=WindowSize.RANDOM,
)
def visit_whatsmyua(driver: Driver, data):
    driver.get("https://www.whatsmyua.info/")
    driver.prompt()

visit_whatsmyua()
```

When working with profiles, you want the fingerprints to remain consistent. You don't want the user's user agent to be Chrome 106 on the first visit and then become Chrome 102 on the second visit. 

So, when using profiles, use the `HASHED` option to generate a consistent user agent and window size based on the profile's hash:

```python
from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from botasaurus.window_size import WindowSize

@browser(
    profile="pikachu",
    user_agent=UserAgent.HASHED,
    window_size=WindowSize.HASHED,
)
def visit_whatsmyua(driver: Driver, data):
    driver.get("https://www.whatsmyua.info/")
    driver.prompt()
    
visit_whatsmyua()

# Everytime Same UserAgent and WindowSize
visit_whatsmyua()
```
#### Passing Arguments to Chrome

To pass arguments to Chrome, use the `add_arguments` option:

```python
@browser(
    add_arguments=['--headless=new'],
)
```

To dynamically generate arguments based on the `data` parameter, pass a function:

```python
def get_arguments(data):
    return ['--headless=new']

@browser(
    add_arguments=get_arguments,
)
```

#### Wait for Complete Page Load

By default, Botasaurus waits for all page resources (DOM, JavaScript, CSS, images, etc.) to load before calling your scraping function with the driver.

However, sometimes the DOM is ready, but JavaScript, images, etc., take forever to load. 

In such cases, you can set `wait_for_complete_page_load` to `False` to interact with the DOM as soon as the HTML is parsed and the DOM is ready:

```python
@browser(
    wait_for_complete_page_load=False,
)
```

#### Reuse Driver

Consider the following example:

```python
from botasaurus.browser import browser, Driver

@browser
def scrape_data(driver: Driver, link):
    driver.get(link)

scrape_data(["https://www.omkar.cloud/", "https://www.omkar.cloud/blog/", "https://stackoverflow.com/"])
```

If you run this code, the browser will be recreated on each page visit, which is inefficient. 

![list-demo-omkar](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/list-demo.gif)

To solve this problem, use the `reuse_driver` option which is great for cases like:
- Scraping a large number of links and reusing the same browser instance for all page visits.
- Running your scraper in a cloud server to scrape data on demand, without recreating Chrome on each request.

Here's how to use `reuse_driver` which will reuse the same Chrome instance for visiting each link.

```python
from botasaurus.browser import browser, Driver

@browser(
    reuse_driver=True
)
def scrape_data(driver: Driver, link):
    driver.get(link)

scrape_data(["https://www.omkar.cloud/", "https://www.omkar.cloud/blog/", "https://stackoverflow.com/"])
```
**Result**
![list-demo-reuse-driver.gif](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/list-demo-reuse-driver.gif)
 
---

Also, by default, whenever the program ends or is canceled, Botasaurus smartly closes any open Chrome instances, leaving no instances running in the background.

In rare cases, you may want to explicitly close the Chrome instance. For such scenarios, you can use the `.close()` method on the scraping function:

```python
scrape_data.close()
```

This will close any Chrome instances that remain open after the scraping function ends.


### How to Significantly Reduce Proxy Costs When Scraping at Scale?

Recently, we had a project requiring access to around 100,000 pages from a well-protected website, necessitating the use of Residential Proxies.

Even after blocking images, we still required 250GB of proxy bandwidth, costing approximately $1050 (at $4.2 per GB with IP Royal). 

This was beyond our budget :(

To solve this, we implemented a smart strategy:
- We first visited the website normally.
- We then made requests for subsequent pages using the browser's `fetch` API.

Since we were only requesting the HTML, which was well compressed by the browser, we reduced our proxy bandwidth needs to just 5GB, costing only $30.

This resulted in savings of around $1000!

Here's an example of how you can do something similar in Botasaurus:

```python
from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify

@browser(
    reuse_driver=True,  # Reuse the browser
    max_retry=5,        # Retry up to 5 times on failure
)
def scrape_data(driver: Driver, link):
    # If the browser is newly opened, first visit the link
    if driver.config.is_new:
        driver.google_get(link)
    
    # Make requests using the browser fetch API
    response = driver.requests.get(link)
    response.raise_for_status()  # Ensure the request was successful
    html = response.text

    # Parse the HTML to extract the desired data
    soup = soupify(html)
    stock_name = soup.select_one('[data-testid="quote-hdr"] h1').get_text()
    stock_price = soup.select_one('[data-testid="qsp-price"]').get_text()
    
    return {
        "stock_name": stock_name,
        "stock_price": stock_price,
    }

# List of URLs to scrape
links = [
    "https://finance.yahoo.com/quote/AAPL/",
    "https://finance.yahoo.com/quote/GOOG/",
    "https://finance.yahoo.com/quote/MSFT/",
]

# Execute the scraping function for the list of links
scrape_data(links)
```

Note:
1. **Dealing with 429 (Too Many Requests) Errors**

   If you encounter a 429 error, add a delay before making another request. Most websites using Nginx, setting a rate limit of 1 request per second. To respect this limit, a delay of 1.13 seconds is recommended.

   ```python
   driver.sleep(1.13)  # Delay to respect the rate limit
   response = driver.requests.get(link)
   ```

2. **Handling 400 Errors Due to Large Cookies**

   If you encounter a 400 error with a "cookie too large" message, delete the cookies and retry the request.

   ```python
   response = driver.requests.get(link)

   if response.status_code == 400:
       driver.delete_cookies()  # Delete cookies to resolve the error
       driver.short_random_sleep()  # Short delay before retrying
       response = driver.requests.get(link)
   ```
3. You can also use `driver.requests.get_mank(links)` to make multiple requests in parallel, which is faster than making them sequentially.

### How to Configure the Browser's Chrome Profile, Language, and Proxy Dynamically Based on Data Parameters?

The decorators in Botasaurus are really flexible, allowing you to pass a function that can derive the browser configuration based on the data item parameter. This is particularly useful when working with multiple Chrome profiles.

You can dynamically configure the browser's Chrome profile and proxy using decorators in two ways:

1. Using functions to extract configuration values from data:
   - Define functions to extract the desired configuration values from the `data` parameter.
   - Pass these functions as arguments to the `@browser` decorator.

   Example:
   ```python
   from botasaurus.browser import browser, Driver

   def get_profile(data):
       return data["profile"]

   def get_proxy(data):
       return data["proxy"]

   @browser(profile=get_profile, proxy=get_proxy)
   def scrape_heading_task(driver: Driver, data):
       profile, proxy = driver.config.profile, driver.config.proxy
       print(profile, proxy)
       return profile, proxy

   data = [
       {"profile": "pikachu", "proxy": "http://142.250.77.228:8000"},
       {"profile": "greyninja", "proxy": "http://142.250.77.229:8000"},
   ]

   scrape_heading_task(data)
   ```

2. Directly passing configuration values when calling the decorated function:
   - Pass the profile and proxy values directly as arguments to the decorated function when calling it.

   Example:
   ```python
   from botasaurus.browser import browser, Driver

   @browser
   def scrape_heading_task(driver: Driver, data):
       profile, proxy = driver.config.profile, driver.config.proxy
       print(profile, proxy)
       return profile, proxy

   scrape_heading_task(
       profile='pikachu',  # Directly pass the profile
       proxy="http://142.250.77.228:8000",  # Directly pass the proxy
   )
   ```

PS: Most Botasaurus decorators allow passing functions to derive configurations from data parameters. Check the decorator's argument type hint to see if it supports this functionality.


### What is the best way to manage profile-specific data like name, age across multiple profiles?

To store data related to the active profile, use `driver.profile`. Here's an example:

```python
from botasaurus.browser import browser, Driver

def get_profile(data):
    return data["profile"]

@browser(profile=get_profile)
def run_profile_task(driver: Driver, data):
    # Set profile data
    driver.profile = {
        'name': 'Amit Sharma',
        'age': 30
    }

    # Update the name in the profile
    driver.profile['name'] = 'Amit Verma'

    # Delete the age from the profile
    del driver.profile['age']

    # Print the updated profile
    print(driver.profile)  # Output: {'name': 'Amit Verma'}

    # Delete the entire profile
    driver.profile = None

run_profile_task([{"profile": "amit"}])
```

For managing all profiles, use the `Profiles` utility. Here's an example:

```python
from botasaurus.profiles import Profiles

# Set profiles
Profiles.set_profile('amit', {'name': 'Amit Sharma', 'age': 30})
Profiles.set_profile('rahul', {'name': 'Rahul Verma', 'age': 30})

# Get a profile
profile = Profiles.get_profile('amit')
print(profile)  # Output: {'name': 'Amit Sharma', 'age': 30}

# Get all profiles
all_profiles = Profiles.get_profiles()
print(all_profiles)  # Output: [{'name': 'Amit Sharma', 'age': 30}, {'name': 'Rahul Verma', 'age': 30}]

# Get all profiles in random order
random_profiles = Profiles.get_profiles(random=True)
print(random_profiles)  # Output: [{'name': 'Rahul Verma', 'age': 30}, {'name': 'Amit Sharma', 'age': 30}] in random order

# Delete a profile
Profiles.delete_profile('amit')
```

Note: All profile data is stored in the `profiles.json` file in the current working directory.
![profiles](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/profiles.png)

### What are some common methods in Botasaurus Driver?

Botasaurus Driver provides several handy methods for web automation tasks, such as:

- Visiting URLs:
  ```python
  driver.get("https://www.example.com")
  driver.google_get("https://www.example.com")  # Use Google as the referer [Recommended]
  driver.get_via("https://www.example.com", referer="https://duckduckgo.com/")  # Use custom referer
  driver.get_via_this_page("https://www.example.com")  # Use current page as referer
  ```

- Finding elements:
  ```python
  from botasaurus.browser import Wait
  search_results = driver.select(".search-results", wait=Wait.SHORT)  # Wait for up to 4 seconds for the element to be present, return None if not found
  all_links = driver.select_all("a")  # Get all elements matching the selector
  search_results = driver.wait_for_element(".search-results", wait=Wait.LONG)  # Wait for up to 8 seconds for the element to be present, raise exception if not found
  hello_mom = driver.get_element_with_exact_text("Hello Mom", wait=Wait.VERY_LONG)  # Wait for up to 16 seconds for an element having the exact text "Hello Mom"
  ```

- Interacting with elements:
  ```python
  driver.type("input[name='username']", "john_doe")  # Type into an input field
  driver.click("button.submit")  # Click an element
  element = driver.select("button.submit")
  element.click()  # Click on an element
  element.select_option("select#fruits", index=2)  # Select an option
  ```

- Retrieving element properties:
  ```python
  header_text = driver.get_text("h1")  # Get text content
  error_message = driver.get_element_containing_text("Error: Invalid input")
  image_url = driver.select("img.logo").get_attribute("src")  # Get attribute value
  ```

- Working with parent-child elements:
  ```python
  parent_element = driver.select(".parent")
  child_element = parent_element.select(".child")
  child_element.click()  # Click child element
  ```

- Executing JavaScript:
  ```python
  result = driver.run_js("script.js") # Run a JavaScript file located in the current working directory.
  result = driver.run_js("return document.title")
  pikachu = driver.run_js("return args.pokemon", {"pokemon": 'pikachu'}) # args can be a dictionary, list, string, etc.
  text_content = driver.select("body").run_js("(el) => el.textContent")
  ```

- Enable human mode to perform, human-like mouse movements and say sayonara to detection:
  ```python
  # Navigate to Cloudflare's Turnstile Captcha demo
  driver.get(
    "https://nopecha.com/demo/cloudflare",
  )

  # Wait for page to fully load
  driver.long_random_sleep()
  
  # Locate iframe containing the Cloudflare challenge
  iframe = driver.get_element_at_point(160, 290)
  
  # Find checkbox element within the iframe
  checkbox = iframe.get_element_at_point(30, 30)

  # Enable human mode for realistic, human-like mouse movements
  driver.enable_human_mode()

  # Click the checkbox to solve the challenge
  checkbox.click()

  # (Optional) Disable human mode if no longer needed  
  driver.disable_human_mode()

  # Pause execution, for inspection
  driver.prompt()
  ```
  
  ![human-mode-demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/human-mode-demo.gif)

- Drag and Drop:
  ```python
  # Open React DnD tutorial  
  driver.get("https://react-dnd.github.io/react-dnd/examples/tutorial")  

  # Select draggable and droppable elements  
  draggable = driver.select('[draggable="true"]')  
  droppable = driver.select('[data-testid="(3,6)"]')  

  # Perform drag-and-drop  
  draggable.drag_and_drop_to(droppable)  

  # Pause execution, for inspection
  driver.prompt()  
  ```

  ![drag-and-drop-demo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/drag-and-drop-demo.gif)

- Selecting Shadow Root Elements:
  ```python
  # Visit the website
  driver.get("https://nopecha.com/demo/cloudflare")
  
  # Wait for page to fully load
  driver.long_random_sleep()
  
  # Locate the element containing shadow root
  shadow_root_element = driver.select('[name="cf-turnstile-response"]').parent
  
  # Access the iframe
  iframe = shadow_root_element.get_shadow_root()

  # Access the nested shadow DOM inside the iframe 
  content = iframe.get_shadow_root()
  
  # print the text content of the "label" element.
  print(content.select("label", wait = 8).text)

  # Pause execution, for inspection
  driver.prompt()
  ```
![Selecting Shadow Root Elements](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/selecting-shadow-root-elements.gif)

- Monitoring requests:
  ```python
  from botasaurus.browser import browser, Driver, cdp

  @browser()
  def scrape_responses_task(driver: Driver, data):
      # Define a handler function that will be called after a response is received
      def after_response_handler(
          request_id: str,
          response: cdp.network.Response,
          event: cdp.network.ResponseReceived,
      ):
          # Extract URL, status, and headers from the response
          url = response.url
          status = response.status
          headers = response.headers
          
          # Print the response details 
          print(
              "after_response_handler",
              {
                  "request_id": request_id,
                  "url": url,
                  "status": status,
                  "headers": headers,
              },
          )

          # Append the request ID to the driver's responses list
          driver.responses.append(request_id)

      # Register the after_response_handler to be called after each response is received
      driver.after_response_received(after_response_handler)

      # Navigate to the specified URL
      driver.get("https://example.com/")

      # Collect all the responses that were appended during the navigation
      collected_responses = driver.responses.collect()
      
      # Save it in output/scrape_responses_task.json
      return collected_responses

  # Execute the scraping task
  scrape_responses_task()
  ```  

- Working with iframes:
  ```python
  driver.get("https://www.freecodecamp.org/news/using-entity-framework-core-with-mongodb/")
  iframe = driver.get_iframe_by_link("www.youtube.com/embed") 
  # OR the following works as well
  # iframe = driver.select_iframe(".embed-wrapper iframe") 
  freecodecamp_youtube_subscribers_count = iframe.select(".ytp-title-expanded-subtitle").text
  print(freecodecamp_youtube_subscribers_count)
  ```
- Executing CDP Command:
  ```python
  from botasaurus.browser import browser, Driver, cdp
  driver.run_cdp_command(cdp.page.navigate(url='https://stackoverflow.blog/open-source'))
  ```

- Miscellaneous:
  ```python
  form.type("input[name='password']", "secret_password")  # Type into a form field
  container.is_element_present(".button")  # Check element presence
  page_html = driver.page_html  # Current page HTML
  driver.select(".footer").scroll_into_view()  # Scroll element into view
  driver.close()  # Close the browser
  ```

### How Can I Pause the Browser to Inspect Website when Developing the Scraper?

To pause the scraper and wait for user input before proceeding, use `driver.prompt()`:

```python
driver.prompt()
```

### How do I configure authenticated proxies with SSL in Botasaurus?

Proxy providers like BrightData, IPRoyal, and others typically provide authenticated proxies in the format "http://username:password@proxy-provider-domain:port". For example, "http://greyninja:awesomepassword@geo.iproyal.com:12321".

However, if you use an authenticated proxy with a library like seleniumwire to visit a website using Cloudflare, or Datadome, you are GUARANTEED to be identified because you are using a non-SSL connection.

To verify this, run the following code:

First, install the necessary packages:
```bash 
python -m pip install selenium_wire
```

Then, execute this Python script:
```python
from seleniumwire import webdriver  # Import from seleniumwire

# Define the proxy
proxy_options = {
    'proxy': {
        'http': 'http://username:password@proxy-provider-domain:port', # TODO: Replace with your own proxy
        'https': 'http://username:password@proxy-provider-domain:port', # TODO: Replace with your own proxy
    }
}

# Install and set up the driver
driver = webdriver.Chrome(seleniumwire_options=proxy_options)

# Visit the desired URL
link = 'https://fingerprint.com/products/bot-detection/'
driver.get("https://www.google.com/")
driver.execute_script(f'window.location.href = "{link}"')

# Prompt for user input
input("Press Enter to exit...")

# Clean up
driver.quit()
```

You will SURELY be identified:

![identified](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/seleniumwireblocked.png)

However, using proxies with Botasaurus solves this issue. See the difference by running the following code:

```python
from botasaurus.browser import browser, Driver

@browser(proxy="http://username:password@proxy-provider-domain:port") # TODO: Replace with your own proxy 
def scrape_heading_task(driver: Driver, data):
    driver.google_get("https://fingerprint.com/products/bot-detection/")
    driver.prompt()

scrape_heading_task()    
```  

Result: 
![not identified](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/botasaurussuccesspage.png)

Important Note: To run the code above, you will need [Node.js](https://nodejs.org/en) installed.

### Why am I getting a socket connection error when using a proxy to access a website?

Certain proxy providers like BrightData will block access to specific websites. To determine if this is the case, run the following code:

```python
from botasaurus.browser import browser, Driver

@browser(proxy="http://username:password@proxy-provider-domain:port")  # TODO: Replace with your own proxy
def visit_what_is_my_ip(driver: Driver, data):
    driver.get("https://whatismyipaddress.com/")
    driver.prompt()

visit_what_is_my_ip()
```

If you can successfully access [whatismyipaddress.com](https://whatismyipaddress.com/) but not the website you're attempting to scrape, it means the proxy provider is blocking access to that particular website. 

In such situations, the only solution is to switch to a different proxy provider.

Some good proxy providers we personally use are:

- For Rotating Datacenter Proxies: 

    - **[requests-ip-rotator](https://pypi.org/project/requests-ip-rotator/):**
    Routes your API requests through AWS API Gateway, leveraging AWS’s large IP pool to automatically rotate IPs. The cost is negligible even for large-scale scraping (millions of pages). **Highly recommended** — this should be your default choice for datacenter proxy rotation.

    - **BrightData Datacenter Proxies:**
    Paid alternative costing around **$0.6 per GB** (pay-as-you-go). Offers a smaller proxy pool compared to AWS.
    
- For Rotating Residential Proxies: **IPRoyal Royal Residential Proxies**, which cost around $7 per GB on a pay-as-you-go basis. No KYC is required.

As always, nothing good in life comes free. Proxies are expensive, and will take up almost all of your scraping costs. 

So, use proxies only when you need them, and prefer request-based scrapers over browser-based scrapers to save bandwidth.

Note: BrightData and IPRoyal have not paid us. We are recommending them based on our personal experience.

### Which country should I choose when using proxies for web scraping?

The United States is often the best choice because:
- The United States has a highly developed internet infrastructure and is home to numerous data centers, ensuring faster internet speeds.
- Most global companies host their websites in the US, so using a US proxy will result in faster scraping speeds.

### Should I use a proxy for web scraping?

ONLY IF you encounter IP blocks.

Sadly, most scrapers unnecessarily use proxies, even when they are not needed. Everything seems like a nail when you have a hammer.

We have seen scrapers which can easily access hundreds of thousands of protected pages using the @browser module on home Wi-Fi without any issues.

So, as a best practice scrape using the @browser module on your home Wi-Fi first. Only resort to proxies when you encounter IP blocks. 

This practice will save you a considerable amount of time (as proxies are really slow) and money (as proxies are expensive as well).

### How to configure the Request Decorator?

The Request Decorator is used to make humane requests. Under the hood, it uses botasaurus-requests, a library based on hrequests, which incorporates important features like:
- Using browser-like headers in the correct order.
- Makes a browser-like connection with correct ciphers.
- Uses `google.com` referer by default to make it appear as if the user has arrived from google search.

Also, The Request Decorator allows you to configure proxy as follows:

```python
@request(
    proxy="http://username:password@proxy-provider-domain:port"
)    
```


### What Options Can I Configure in all 3 Decorators?

All 3 decorators allow you to configure the following options:

- Parallel Execution:
- Caching Results
- Passing Common Metadata
- Asynchronous Queues
- Asynchronous Execution
- Handling Crashes
- Configuring Output
- Exception Handling

Let's dive into each of these options and in later sections we will see their real-world applications.

#### `parallel`

The `parallel` option allows you to scrape data in parallel by launching multiple browser/request/task instances simultaneously. This can significantly speed up the scraping process.

Run the example below to see parallelization in action:
```python
from botasaurus.browser import browser, Driver

@browser(parallel=3, data=["https://stackoverflow.blog/open-source", "https://stackoverflow.blog/ai", "https://stackoverflow.blog/productivity",])
def scrape_heading_task(driver: Driver, link):
    driver.get(link)
    heading = driver.get_text('h1')
    return heading

scrape_heading_task()    
```

#### `cache`

The `cache` option enables caching of web scraping results to avoid re-scraping the same data. This can significantly improve performance and reduce redundant requests.


Run the example below to see how caching works:
```python
from botasaurus.browser import browser, Driver

@browser(cache=True, data=["https://stackoverflow.blog/open-source", "https://stackoverflow.blog/ai", "https://stackoverflow.blog/productivity",])
def scrape_heading_task(driver: Driver, link):
    driver.get(link)
    heading = driver.get_text('h1')
    return heading

print(scrape_heading_task())
print(scrape_heading_task())  # Data will be fetched from cache immediately 
```

Note: Caching is one of the most important features of Botasaurus.

#### `metadata`

The metadata option allows you to pass common information shared across all data items. This can include things like API keys, browser cookies, or any other data that remains constant throughout the scraping process.

It is commonly used with caching to exclude details like API keys and browser cookies from the cache key.

Here's an example of how to use the `metadata` option:
```python
from botasaurus.task import task

@task()
def scrape_heading_task(data, metadata):
    print("metadata:", metadata)
    print("data:", data)

data = [
    {"profile": "pikachu", "proxy": "http://142.250.77.228:8000"},
    {"profile": "greyninja", "proxy": "http://142.250.77.229:8000"},
]
scrape_heading_task(
  data, 
  metadata={"api_key": "BDEC26..."}
)
```

#### `async_queue`

In the world of web scraping, there are only two types of scrapers:

1. Dataset Scrapers: These extract data from websites and store it as datasets. Companies like Bright Data use them to build datasets for Crunchbase, Indeed, etc.

2. Real-time Scrapers: These fetch data from sources in real-time, like SERP APIs that provide Google and DuckDuckGo search results.

When building real-time scrapers, speed is paramount because customers are waiting for requests to complete. The `async_queue` feature is incredibly useful in such cases.

`async_queue` allows you to run scraping tasks asynchronously in a queue and gather the results using the `.get()` method. 

A great use case for `async_queue` is scraping Google Maps. Instead of scrolling through the list of places and then scraping the details of each place sequentially, you can use `async_queue` to:
1. Scroll through the list of places.
2. Simultaneously make HTTP requests to scrape the details of each place in the background.
    
By executing the scrolling and requesting tasks concurrently, you can significantly speed up the scraper.

Run the code below to see browser scrolling and request scraping happening concurrently (really cool, must try!):
```python
from botasaurus.browser import browser, Driver, AsyncQueueResult
from botasaurus.request import request, Request
import json

def extract_title(html):
    return json.loads(
        html.split(";window.APP_INITIALIZATION_STATE=")[1].split(";window.APP_FLAGS")[0]
    )[5][3][2][1]

@request(
    parallel=5,
    async_queue=True,
    max_retry=5,
)
def scrape_place_title(request: Request, link, metadata):
    cookies = metadata["cookies"]
    html = request.get(link, cookies=cookies, timeout=12).text
    title = extract_title(html)
    print("Title:", title)
    return title

def has_reached_end(driver):
    return driver.select('p.fontBodyMedium > span > span') is not None

def extract_links(driver):
    return driver.get_all_links('[role="feed"] > div > div > a')

@browser()
def scrape_google_maps(driver: Driver, link):
    driver.google_get(link, accept_google_cookies=True)  # accepts google cookies popup

    scrape_place_obj: AsyncQueueResult = scrape_place_title()  # initialize the async queue for scraping places
    cookies = driver.get_cookies_dict()  # get the cookies from the driver

    while True:
        links = extract_links(driver)  # get the links to places
        scrape_place_obj.put(links, metadata={"cookies": cookies})  # add the links to the async queue for scraping

        print("scrolling")
        driver.scroll_to_bottom('[role="feed"]')  # scroll to the bottom of the feed

        if has_reached_end(driver):  # we have reached the end, let's break buddy
            break

    results = scrape_place_obj.get()  # get the scraped results from the async queue
    return results

scrape_google_maps("https://www.google.com/maps/search/web+developers+in+bangalore")
```

#### `run_async`

Similarly, the `run_async` option allows you to execute scraping tasks asynchronously, enabling concurrent execution.

Similar to `async_queue`, you can use the `.get()` method to retrieve the results of an asynchronous task.

Code Example:
```python
from botasaurus.browser import browser, Driver
from time import sleep

@browser(run_async=True)
def scrape_heading(driver: Driver, data):
    sleep(5)
    return {}

if __name__ == "__main__":
    result1 = scrape_heading()  # Launches asynchronously
    result2 = scrape_heading()  # Launches asynchronously

    result1.get()  # Wait for the first result
    result2.get()  # Wait for the second result
```

#### `close_on_crash`

The `close_on_crash` option determines the behavior of the scraper when an exception occurs:
- If set to `False` (default):
  - The scraper will make a beep sound and pause the browser.
  - This makes debugging easier by keeping the browser open at the point of the crash.
  - Use this setting during development and testing.
- If set to `True`:
  - The scraper will close the browser and continue with the rest of the data items.
  - This is suitable for production environments when you are confident that your scraper is robust.
  - Use this setting to avoid interruptions and ensure the scraper processes all data items.

```python
from botasaurus.browser import browser, Driver

@browser(
    close_on_crash=False  # Determines whether the browser is paused (default: False) or closed when an error occurs
)
def scrape_heading_task(driver: Driver, data):
    raise Exception("An error occurred during scraping.")

scrape_heading_task()  
```

#### `output` and `output_formats`

By default, Botasaurus saves the result of scraping in the `output/{your_scraping_function_name}.json` file. Let's learn about various ways to configure the output.

1. **Change Output Filename**: Use the `output` parameter in the decorator to specify a custom filename for the output.
```python
from botasaurus.task import task

@task(output="my-output")
def scrape_heading_task(data): 
    return {"heading": "Hello, Mom!"}

scrape_heading_task()
```

2. **Disable Output**: If you don't want any output to be saved, set `output` to `None`.
```python
from botasaurus.task import task

@task(output=None)
def scrape_heading_task(data): 
    return {"heading": "Hello, Mom!"}

scrape_heading_task()
```

3. **Dynamically Write Output**: To dynamically write output based on data and result, pass a function to the `output` parameter:
```python
from botasaurus.task import task
from botasaurus import bt

def write_output(data, result):
    json_filename = bt.write_json(result, 'data')
    excel_filename = bt.write_excel(result, 'data')
    bt.zip_files([json_filename, excel_filename]) # Zip the JSON and Excel files for easy delivery to the customer

@task(output=write_output)  
def scrape_heading_task(data): 
    return {"heading": "Hello, Mom!"}

scrape_heading_task()
```

4. **Upload File to S3**: Use `bt.upload_to_s3` to upload file to S3 bucket.
```python
from botasaurus.task import task
from botasaurus import bt

def write_output(data, result):
    json_filename = bt.write_json(result, 'data')
    bt.upload_to_s3(json_filename, 'my-magical-bucket', "AWS_ACCESS_KEY", "AWS_SECRET_KEY")

@task(output=write_output)  
def scrape_heading_task(data): 
    return {"heading": "Hello, Mom!"}

scrape_heading_task()
```

5.**Save Outputs in Multiple Formats**: Use the `output_formats` parameter to save outputs in different formats like JSON and EXCEL.
```python
from botasaurus.task import task

@task(output_formats=[bt.Formats.JSON, bt.Formats.EXCEL])  
def scrape_heading_task(data): 
    return {"heading": "Hello, Mom!"}

scrape_heading_task()
```

PRO TIP: When delivering data to customers, provide the dataset in JSON and Excel formats. Avoid CSV unless the customer asks, because Microsoft Excel has a hard time rendering CSV files with nested JSON.

**CSV vs Excel**
![csv-vs-excel](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/csv-vs-excel.png)

#### Exception Handling Options

Botasaurus provides various exception handling options to make your scrapers more robust:
- `max_retry`: By default, any failed task is not retried. You can specify the maximum number of times to retry scraping when an error occurs using the `max_retry` option.
- `retry_wait`: Specifies the waiting time between retries.
- `raise_exception`: By default, Botasaurus does not raise an exception when an error occurs during scraping, because let's say you are keeping your PC running overnight to scrape 10,000 links. If one link fails, you really don't want to stop the entire scraping process, and ruin your morning by seeing an unfinished dataset.
- `must_raise_exceptions`: Specifies exceptions that must be raised, even if `raise_exception` is set to `False`.
- `create_error_logs`: Determines whether error logs should be created when exceptions occur. In production, when scraping hundreds of thousands of links, it's recommended to set `create_error_logs` to `False` to avoid using computational resources for creating error logs.

```python
@browser(
    raise_exception=True,  # Raise an exception and halt the scraping process when an error occurs
    max_retry=5,  # Retry scraping a failed task a maximum of 5 times
    retry_wait=10,  # Wait for 10 seconds before retrying a failed task
    must_raise_exceptions=[CustomException],  # Definitely raise CustomException, even if raise_exception is set to False
    create_error_logs=False  # Disable the creation of error logs to optimize scraper performance
)
def scrape_heading_task(driver: Driver, data):
  # ...
```

### What are some examples of common web scraping utilities provided by Botasaurus that make scraping easier?

#### bt Utility

The `bt` utility provides helper functions for:

- Writing and reading JSON, EXCEL, and CSV files
- Data cleaning

Some key functions are:

- `bt.write_json` and `bt.read_json`: Easily write and read JSON files.
```python
from botasaurus import bt

data = {"name": "pikachu", "power": 101}
bt.write_json(data, "output")
loaded_data = bt.read_json("output")
```

- `bt.write_excel` and `bt.read_excel`: Easily write and read EXCEL files.
```python
from botasaurus import bt

data = {"name": "pikachu", "power": 101}
bt.write_excel(data, "output")
loaded_data = bt.read_excel("output")
```

- `bt.write_csv` and `bt.read_csv`: Easily write and read CSV files.
```python
from botasaurus import bt

data = {"name": "pikachu", "power": 101}
bt.write_csv(data, "output")
loaded_data = bt.read_csv("output")
```

- `bt.write_html` and `bt.read_html`: Write HTML content to a file.
```python
from botasaurus import bt

html_content = "<html><body><h1>Hello, Mom!</h1></body></html>"
bt.write_html(html_content, "output")
```

- `bt.write_temp_json`, `bt.write_temp_csv`, `bt.write_temp_html`: Write temporary JSON, CSV, or HTML files for debugging purposes.
```python
from botasaurus import bt

data = {"name": "pikachu", "power": 101}
bt.write_temp_json(data)
bt.write_temp_csv(data)
bt.write_temp_html("<html><body><h1>Hello, Mom!</h1></body></html>")
```

- Data cleaning functions like `bt.extract_numbers`, `bt.extract_links`, `bt.remove_html_tags`, and more.
```python
text = "The price is $19.99 and the website is https://www.example.com"
numbers = bt.extract_numbers(text)  # [19.99]
links = bt.extract_links(text)  # ["https://www.example.com"]
```

#### Local Storage Utility

The Local Storage utility allows you to store and retrieve key-value pairs, which can be useful for maintaining state between scraper runs. 

Here's how to use it:

```python
from botasaurus.local_storage import LocalStorage

LocalStorage.set_item("credits_used", 100)
print(LocalStorage.get_item("credits_used", 0))
```

#### soupify Utility

The `soupify` utility creates a BeautifulSoup object from a Driver, Requests response, Driver Element, or HTML string.

```python
from botasaurus.soupify import soupify
from botasaurus.request import request, Request
from botasaurus.browser import browser, Driver

@request
def get_heading_from_request(req: Request, data):
   """
   Get the heading of a web page using the request object.
   """
   response = req.get("https://www.example.com")
   soup = soupify(response)
   heading = soup.find("h1").text
   print(f"Page Heading: {heading}")

@browser
def get_heading_from_driver(driver: Driver, data):
   """
   Get the heading of a web page using the driver object.
   """
   driver.get("https://www.example.com")

   # Get the heading from the entire page
   page_soup = soupify(driver)
   page_heading = page_soup.find("h1").text
   print(f"Heading from Driver's Soup: {page_heading}")

   # Get the heading from the body element
   body_soup = soupify(driver.select("body"))
   body_heading = body_soup.find("h1").text
   print(f"Heading from Element's Soup: {body_heading}")

# Call the functions
get_heading_from_request()
get_heading_from_driver()
```

#### IP Utils

IP Utils provide functions to get information about the current IP address, such as the IP itself, country, ISP, and more:

```python
from botasaurus.ip_utils import IPUtils

# Get the current IP address
current_ip = IPUtils.get_ip()
print(current_ip)
# Output: 47.31.226.180

# Get detailed information about the current IP address
ip_info = IPUtils.get_ip_info()
print(ip_info)
# Output: {
#     "ip": "47.31.226.180",
#     "country": "IN",
#     "region": "Delhi",
#     "city": "Delhi",
#     "postal": "110001",
#     "coordinates": "28.6519,77.2315",
#     "latitude": "28.6519",
#     "longitude": "77.2315",
#     "timezone": "Asia/Kolkata",
#     "org": "AS55836 Reliance Jio Infocomm Limited"
# }
```

#### Cache Utility
The Cache utility in Botasaurus allows you to manage cached data for your scraper. You can put, get, has, remove, and clear cache data.

*Basic Usage*

```python
from botasaurus.task import task
from botasaurus.cache import Cache

# Example scraping function
@task
def scrape_data(data):
    # Your scraping logic here
    return {"processed": data}

# Sample data for scraping
input_data = {"key": "value"}

# Adding data to the cache
Cache.put('scrape_data', input_data, scrape_data(input_data))

# Checking if data is in the cache
if Cache.has('scrape_data', input_data):
    # Retrieving data from the cache
    cached_data = Cache.get('scrape_data', input_data)
    print(f"Cached data: {cached_data}")

# Removing specific data from the cache
Cache.remove('scrape_data', input_data)

# Clearing the complete cache for the scrape_data function
Cache.clear('scrape_data')
```

**Advanced Usage for large-scale scraping projects**

*Count Cached Items*

You can count the number of items cached for a particular function, which can serve as a scraping progress bar.

```python
from botasaurus.cache import Cache

Cache.print_cached_items_count('scraping_function')
```

*Filter Cached/Uncached Items*

You can filter items that have been cached or not cached for a particular function.

```python
from botasaurus.cache import Cache

all_items = ['1', '2', '3', '4', '5']

# Get items that are cached
cached_items = Cache.filter_items_in_cache('scraping_function', all_items)
print(cached_items)

# Get items that are not cached
uncached_items = Cache.filter_items_not_in_cache('scraping_function', all_items)
print(uncached_items)
```

*Delete Cache*
The cache for a function is stored in the `cache/{your_scraping_function_name}/` folder. To delete the cache, simply delete that folder.

![delete-cache](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-cache.png)


*Delete Specific Items*

You can delete specific items from the cache for a particular function.

```python
from botasaurus.cache import Cache

all_items = ['1', '2', '3', '4', '5']
deleted_count = Cache.delete_items('scraping_function', all_items)
print(f"Deleted {deleted_count} items from the cache.")
```

*Delete Items by Filter*  

In some cases, you may want to delete specific items from the cache based on a condition. For example, if you encounter honeypots (mock HTML served to dupe web scrapers) while scraping a website, you may want to delete those items from the cache.

```python
def should_delete_item(item, result):
    if 'Honeypot Item' in result:
        return True  # Delete the item
    return False  # Don't delete the item

all_items = ['1', '2', '3', '4', '5']
# List of items to iterate over, it is fine if the list contains items which have not been cached, as they will be simply ignored.
Cache.delete_items_by_filter('scraping_function', should_delete_item, all_items)
```

Importantly, be cautious and first use `delete_items_by_filter` on a small set of items which you want to be deleted. Here's an example:

```python
from botasaurus import bt
from botasaurus.cache import Cache

def should_delete_item(item, result):
    # TODO: Update the logic
    if 'Honeypot Item' in result:
        return True # Delete the item
    return False # Don't delete the item

test_items = ['1', '2'] # TODO: update with target items
scraping_function_name = 'scraping_function' # TODO:  update with target scraping function name
Cache.delete_items_by_filter(scraping_function_name, test_items, should_delete_item)

for item in test_items:
    if Cache.has(scraping_function_name, item):
        bt.prompt(f"Item {item} was not deleted. Please review the logic of the should_delete_item function.")
```

### How to Extract Links from a Sitemap?

In web scraping, it is a common use case to scrape product pages, blogs, etc. But before scraping these pages, you need to get the links to these pages.

Sadly, many developers unnecessarily increase their work by writing code to visit each page one by one and scrape links, which they could have easily obtained by just looking at the Sitemap.

The Botasaurus Sitemap Module makes this process easy as cake by allowing you to get all links or sitemaps using:
- The homepage URL (e.g., `https://www.omkar.cloud/`)
- A direct sitemap link (e.g., `https://www.omkar.cloud/sitemap.xml`)
- A `.gz` compressed sitemap

For example, if you're an Angel Investor seeking innovative tech startups to invest in, G2 is an ideal platform to find such startups. You can run the following code to fetch over 190K+ product links from G2:

```python
from botasaurus import bt
from botasaurus.sitemap import Sitemap, Filters, Extractors

links = (
    Sitemap("https://www.g2.com/sitemaps/sitemap_index.xml.gz")
    .filter(Filters.first_segment_equals("products"))
    .extract(Extractors.extract_link_upto_second_segment())
    .write_links('g2-products')
)
```

**Output:** 

![g2-sitemap-links.png](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/g2-sitemap-links.png)

Or, let's say you're in the mood for some reading and looking for good stories. The following code will get you over 1000+ stories from [moralstories26.com](https://moralstories26.com/):

```python
from botasaurus import bt
from botasaurus.sitemap import Sitemap, Filters

links = (
    Sitemap("https://moralstories26.com/")
    .filter(
        Filters.has_exactly_1_segment(),
        Filters.first_segment_not_equals(
            ["about", "privacy-policy", "akbar-birbal", "animal", "education", "fables", "facts", "family", "famous-personalities", "folktales", "friendship", "funny", "heartbreaking", "inspirational", "life", "love", "management", "motivational", "mythology", "nature", "quotes", "spiritual", "uncategorized", "zen"]
        ),
    )
    .write_links('moral-stories')
)
```

**Output:** 

![moralstories26-sitemap-links.png](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/moralstories26-sitemap-links.png)

Also, before scraping a site, it's useful to identify the available sitemaps. This can be easily done with the following code:

```python
from botasaurus import bt
from botasaurus.sitemap import Sitemap

sitemaps = Sitemap("https://www.omkar.cloud/").write_sitemaps('omkar-sitemaps')
```

**Output:** 

![omkar-sitemap-links.png](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/omkar-sitemap-links.png)

To ensure your scrapers run super fast, we cache the Sitemap, but you may want to periodically refresh the cache. To do so, pass the Cache.REFRESH parameter. 

```python
from botasaurus import bt
from botasaurus.sitemap import Sitemap, Filters, Extractors
from botasaurus.cache import Cache

links = (
    Sitemap("https://moralstories26.com/", cache=Cache.REFRESH)
    .write_links('moral-stories')
)
```
### How can I filter a list of links, similar to working with Sitemaps?

Filtering links from a webpage is a common requirement in web scraping. For example, you might want to filter out all non-product pages.


Botasaurus's `Links` module simplifies link filtering and extraction:

```python
from botasaurus.links import Links, Filters, Extractors

# Sample list of links
links = [
    "https://finance.yahoo.com/topic/stock-market-news/",
    "https://finance.yahoo.com/topic/morning-brief/", 
    "https://finance.yahoo.com/quote/AAPL/", 
    "https://finance.yahoo.com/quote/GOOG/"
]

# Filter and extract links
filtered_links = (
    Links(links)
    .filter(Filters.first_segment_equals("quote"))
    .extract(Extractors.extract_link_upto_second_segment())
    .write('stocks')
)
```

### What is the best way to use caching in Botasaurus?

Sadly, when using caching, most developers write a scraping function that scrapes the HTML and extracts the data from the HTML in the same function, like this:

```python
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def scrape_data(request: Request, data):
    # Visit the Link
    response = request.get(data)
    
    # Create a BeautifulSoup object
    soup = soupify(response)
    
    # Retrieve the heading element's text
    heading = soup.find('h1').get_text()
    
    # Save the data as a JSON file in output/scrape_data.json
    return {"heading": heading}

data_items = [
    "https://stackoverflow.blog/open-source",
    "https://stackoverflow.blog/ai",
    "https://stackoverflow.blog/productivity",
]

scrape_data(data_items)
```

Now, let's say, after 50% of the dataset has been scraped, what if:
- Your customer wants to add another data point (which is very likely), or
- One of your BeautifulSoup selectors happens to be flaky and needs to be updated (which is super likely)?

In such cases, you will have to scrape all the pages again, which is painful as it will take a lot of time and incur high proxy costs.

To resolve this issue, you can:
1. Write a function that only scrapes and caches the HTML.
2. Write a separate function that calls the HTML scraping function, extracts data using BeautifulSoup, and caches the result.

Here's a practical example:

```python
from bs4 import BeautifulSoup
from botasaurus.task import task
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request(cache=True)
def scrape_html(request: Request, link):
    # Scrape the HTML and cache it
    html = request.get(link).text
    return html

def extract_data(soup: BeautifulSoup):
    # Extract the heading from the HTML
    heading = soup.find("h1").get_text()
    return {"heading": heading}

# Cache the scrape_data task as well
@task(cache=True)
def scrape_data(link):
    # Call the scrape_html function to get the cached HTML
    html = scrape_html(link)
    # Extract data from the HTML using the extract_data function
    return extract_data(soupify(html))

data_items = [
    "https://stackoverflow.blog/open-source",
    "https://stackoverflow.blog/ai",
    "https://stackoverflow.blog/productivity",
]

scrape_data(data_items)
```

With this approach:
- If you need to add data points or fix BeautifulSoup bugs, delete the `cache/scrape_data` folder and re-run the scraper.
![delete-cache](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-cache.png)
- You only need to re-run the BeautifulSoup extraction, not the entire HTML scraping, saving time and proxy costs. Yahoo!

**PRO TIP**: This approach also makes your `extract_data` code easier and faster to test, like this:

```python
from bs4 import BeautifulSoup
from botasaurus import bt

def extract_data(soup: BeautifulSoup):
    heading = soup.find('h1').get_text()
    return {"heading": heading}

if __name__ == '__main__':
    # Will use the cached HTML and run the extract_data function again.
    bt.write_temp_json(scrape_data("https://stackoverflow.blog/open-source", cache=False))
```
### What are the recommended settings for each decorator to build a production-ready scraper in Botasaurus?

For websites with minimal protection, use the `Request` module.

Here's a template for creating production-ready datasets using the `Request` module:

```python
from bs4 import BeautifulSoup
from botasaurus.task import task
from botasaurus.request import request, Request,NotFoundException
from botasaurus.soupify import soupify

@request(
    # proxy='http://username:password@datacenter-proxy-domain:proxy-port', # Uncomment to use Proxy ONLY if you face IP blocking
    cache=True,

    max_retry=20, # Retry up to 20 times, which is a good default

    output=None,

    close_on_crash=True,
    raise_exception=True,
    create_error_logs=False,
)
def scrape_html(request: Request, link):
    # Scrape the HTML and cache it
    response = request.get(link)
    if response.status_code == 404:
        # A Special Exception to skip retrying this link
        raise NotFoundException(link)
    response.raise_for_status()
    return response.text

def extract_data(soup: BeautifulSoup):
    # Extract the heading from the HTML
    heading = soup.find("h1").get_text()
    return {"heading": heading}

# Cache the scrape_data task as well
@task(
    cache=True,
    close_on_crash=True,
    create_error_logs=False,
    parallel=40, # Run 40 requests in parallel, which is a good default
)
def scrape_data(link):
    # Call the scrape_html function to get the cached HTML
    html = scrape_html(link)
    # Extract data from the HTML using the extract_data function
    return extract_data(soupify(html))

data_items = [
    "https://stackoverflow.blog/open-source",
    "https://stackoverflow.blog/ai",
    "https://stackoverflow.blog/productivity",
]

scrape_data(data_items)
```

For visiting well protected websites, use the `Browser` module. 

Here's a template for creating production-ready datasets using the `Browser` module:

```python
from bs4 import BeautifulSoup
from botasaurus.task import task
from botasaurus.browser import browser, Driver, NotFoundException
from botasaurus.soupify import soupify

@browser(
    # proxy='http://username:password@datacenter-proxy-domain:proxy-port', # Uncomment to use Proxy ONLY if you face IP blocking

    # block_images_and_css=True, # Uncomment to block images and CSS, which can speed up scraping
    # wait_for_complete_page_load=False, # Uncomment to proceed once the DOM (Document Object Model) is loaded, without waiting for all resources to finish loading. This is recommended for faster scraping of Server Side Rendered (HTML) pages.

    cache=True,
    max_retry=5,  # Retry up to 5 times, which is a good default

    reuse_driver= True, # Reuse the same driver for all tasks
    
    output=None,

    close_on_crash=True,
    raise_exception=True,
    create_error_logs=False,
)
def scrape_html(driver: Driver, link):
    # Scrape the HTML and cache it
    if driver.config.is_new:
        driver.google_get(
            link,
            bypass_cloudflare=True,  # delete this line if the website you're accessing is not protected by Cloudflare
        )
    response = driver.requests.get(link)
    
    if response.status_code == 404:
        # A Special Exception to skip retrying this link
        raise NotFoundException(link)
    response.raise_for_status()
    
    html = response.text        
    return html

def extract_data(soup: BeautifulSoup):
    # Extract the heading from the HTML
    stock_name = soup.select_one('[data-testid="quote-hdr"] h1').get_text()
    stock_price = soup.select_one('[data-testid="qsp-price"]').get_text()
    
    return {
        "stock_name": stock_name,
        "stock_price": stock_price,
    }

# Cache the scrape_data task as well
@task(
    cache=True,
    close_on_crash=True,
    create_error_logs=False,
)
def scrape_data(link):
    # Call the scrape_html function to get the cached HTML
    html = scrape_html(link)
    # Extract data from the HTML using the extract_data function
    return extract_data(soupify(html))

data_items = [
    "https://finance.yahoo.com/quote/AAPL/",
    "https://finance.yahoo.com/quote/GOOG/",
    "https://finance.yahoo.com/quote/MSFT/",
]

scrape_data(data_items)
```

### Why Am I Getting Detected on Some Websites?

If you're getting detected, it's likely due to:

- Using a non-residential proxy — Services like Datadome and Cloudflare often flag datacenter IPs/VPNs.
- Clicking without Human Mode enabled — Unnatural mouse movements can trigger detection.
- Visiting websites too quickly — Rapid, bot-like navigation is easy to detect.

To reduce detection, follow these best practices:

1. Upgrade all Botasaurus packages to the latest version:
   ```bash
   python -m pip install --upgrade bota botasaurus botasaurus-api botasaurus-requests botasaurus-driver botasaurus-proxy-authentication botasaurus-server botasaurus-humancursor
   ```

2. Enable Human Mode for human-like mouse movements:
   ```python
   driver.enable_human_mode()
   ```

3. Avoid rapid `driver.get` calls. Instead, try:
   - Clicking within pages with Human Mode enabled, if possible.
   - Using `driver.google_get` or `driver.get_via_this_page`.
   - Using [`driver.requests.get`](https://github.com/omkarcloud/botasaurus?tab=readme-ov-file#how-to-significantly-reduce-proxy-costs-when-scraping-at-scale) to fetch the page HTML content.

4. Slow down your scraper with random delays:
   ```python
   driver.short_random_sleep()
   driver.long_random_sleep()
   ```

5. Avoid using `headless` mode, as it can be easily detected by Cloudflare, Datadome, and Imperva.

6. Use a residential proxy, as datacenter IPs are often flagged.

7. Remove the `--no-default-browser-check` argument as it is detectable by systems like Datadome, as follows:
   ```python
   @browser(remove_default_browser_check_argument=True)
   ```

8. If your IP has been flagged, you can perform this technique to change it:
1. Visit [whatismyipaddress.com](https://whatismyipaddress.com/) to see your current IP Address.
2. Connect your PC to a smartphone's hotspot.
3. On your smartphone, turn airplane mode on and off.
4. Turn the hotspot on again.
5. Now visit [whatismyipaddress.com](https://whatismyipaddress.com/). You'll see a new IP address.

### How Do I Close All Running Chrome Instances?

While developing a scraper, multiple browser instances may remain open in the background (because of interrupting it with CTRL + C). This situation can cause your computer to hang.

![Many Chrome processes running in Task Manager](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/chrome-running.png)

To prevent your PC from hanging, you can run the following command to close all Chrome instances:

```shell
python -m close_chrome
```

### How to Run Scraper in Docker?

To run a Scraper in Docker, use the Botasaurus Starter Template, which includes the necessary Dockerfile and Docker Compose configurations.

Use the following commands to clone the Botasaurus Starter Template, build a Docker image from it, and execute the scraper within a Docker environment.

```
git clone https://github.com/omkarcloud/botasaurus-starter my-botasaurus-project
cd my-botasaurus-project
docker-compose build
docker-compose up
```

### How to Run Scraper in Gitpod?

Running a scraper in Gitpod offers several benefits:

- Allows your scraper to use a powerful 8-core machine with 1000 Mbps internet speed
- Makes it easy to showcase your scraper to customers without them having to install anything, by simply sharing the Gitpod machine link

In this example, we will run the Botasaurus Starter template in Gitpod:

1. First, visit [this link](https://gitpod.io/#https://github.com/omkarcloud/botasaurus-starter) and sign up using your GitHub account.
   
   ![Screenshot (148)](https://raw.githubusercontent.com/omkarcloud/google-maps-scraper/master/screenshots/open-in-gitpod.png)
  
2. Once signed up, open the starter project in Gitpod.   

   ![gp-continue](https://raw.githubusercontent.com/omkarcloud/assets/master/images/gitpod-continue.png)

3. To use UI Scraper, run the following command in Terminal:
   ```bash
   python run.py
   ```
4. You will see a popup notification with the heading "A service is available on port 3000". In the popup notification, click the **"Open Browser"** button to open the UI Dashboard in your browser

   ![open-browser.png](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/open-browser.png)

5. Now, you can press the `Run` button to get the results.
   
   ![starter-photo.png](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/starter-photo.png)

Note: Gitpod is not suitable for long-running tasks, as the environment will automatically shut down after a short period of inactivity. Use your local machine or a cloud VM for long-running scrapers.

## Should I Scrape Datasets Locally or in the Cloud?  
For most scraping tasks, we recommend running the scraper **locally** on your system because:  
- It requires far fewer setup steps  
- It saves time and costs  
- Most importantly, it allows you to quickly fix bugs and continue scraping.

However, consider cloud scraping when:  
- Running tasks longer than 5 days.  
- Scraping large-scale data (terabytes).  
- Performing recurring monthly scrapes.  
- Having slow Internet or data caps

Cloud scraping is also significantly faster due to superior internet speeds (often 10x+ faster than home Wi-Fi).  

---

## How to Run a Data Scraper in a Virtual Machine? 

To run a scraper in a virtual machine (VM), follow these steps:

### 1. Prepare Your Scraper
1. Use the [Botasaurus Starter Template](https://github.com/omkarcloud/botasaurus-starter) to create your dataset scraper.
2. For large datasets, ensure memory efficiency (e.g., by using file formats like `ndjson`).  
3. Add project dependencies to `requirements.txt`.
4. Push your project to GitHub.

### 2. Set Up a Virtual Machine

1. If you don't already have one, create a Google Cloud Account. You'll receive a $300 credit to use over 3 months.
   ![Select-your-billing-country](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/Select-your-billing-country.png)


2. Go to [Google Click to Deploy](https://console.cloud.google.com/marketplace/product/click-to-deploy-images/nodejs), create a deployment and configure it as follows or as appropriate based on your workload:
   ```
   Zone: us-central1-a # Use us-central1 (Iowa) for the lowest-cost VMs
   Series: N1
   Machine Type: n1-standard-2 (2 vCPU, 1 core, 7.5 GB memory)
   Boot Disk Type: Standard persistent disk	# This is the most cost-effective disk option.
   Boot disk size in GB: 20 GB # Adjust based on storage needs  
   ```
   ![Deployment setup](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/deploy-node-vm.gif)

3. Navigate to [VM Instances](https://console.cloud.google.com/compute/instances) and click the SSH button to SSH into the VM.
   ![ssh-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/ssh-vm.png)

4.  Now, run the following command in the terminal and wait for it to complete:

   ```bash
   curl -sL https://raw.githubusercontent.com/omkarcloud/botasaurus/master/vm-scripts/install-bota.sh | bash
   ```
   
5.  Install your scraper by running the following command. It may take 5 minutes to install the scraper, so grab a coffee or watch [this awesome video](https://www.youtube.com/watch?v=nwAYpLVyeFU):

   ```bash
   python3 -m bota install-scraper --repo-url https://github.com/omkarcloud/botasaurus-starter
   ```
   ![install-scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-scraper-vm.gif)

   Note: If you are using a different repo, replace `https://github.com/omkarcloud/botasaurus-starter` with your repo URL.
   
That's it! You have successfully installed the scraper in a virtual machine. The scraper will now start running and succeed.

![ls-output](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/vm-succeed.png)

*Notes*
- The `main.py` file serves as the scraper's entry point.
- Update your project's `requirements.txt` to ensure it has all the dependencies required to run the scraper.
- Ensure your VM has enough memory for your scraper's needs.
- If running a headful browser, enable a virtual display by setting `enable_xvfb_virtual_display=True`. This creates a virtual display required for running a headful browser in a VM.
  ```python
  @browser(enable_xvfb_virtual_display=True)
  ```
- The scraper will run until it completes successfully or fails three times. You can also configure retries as follows:
  For example, to allow a maximum of 5 retries:
  ```bash
  python3 -m bota install-scraper --repo-url <your-repo> --max-retry=5
  ```
  or, to allow unlimited retries:
  ```bash
  python3 -m bota install-scraper --repo-url <your-repo> --max-retry=unlimited
  ```
- If your scraper fails, you can check the logs of the current boot by running:
  ```bash
  journalctl -u botasaurus-starter.service -b # replace botasaurus-starter with your repo name
  ```

*Downloading Data*
To download the scraped data, you can either:
1. Download it directly from the VM.
![Download Data from VM](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/download-data-vm.png)
2. Upload it to Amazon S3:
   ```python
   from botasaurus import bt
   bt.upload_to_s3('data.json', 'my-bucket', "AWS_ACCESS_KEY", "AWS_SECRET_KEY")
   ```

## How to Stop the Scraper
If you are performing recurring monthly scrapes, it's best to stop the scraper instead of deleting it. Note that you will only incur storage costs (~$0.4 per month for a 10GB Standard Persistent Disk) but not compute costs.

To stop the scraper:
1. Visit [VM Instances](https://console.cloud.google.com/compute/instances).
2. Select your VM and stop it.

![stop-scraper-in-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stop-scraper-in-vm.png)

To restart later:
1. Start the VM from [VM Instances](https://console.cloud.google.com/compute/instances).

![run-scraper-in-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/run-scraper-in-vm.png)
2. SSH into it.
3. Delete caches and update sitemaps if needed.
4. Restart with:
   ```bash
   shutdown -r now
   ```

## How to Delete the Scraper and Avoid Incurring Further Charges

If you no longer need the scraper, please ensure you have downloaded your data before deleting it.

Next, follow these steps to delete the scraper:
1. Go to [Deployments](https://console.cloud.google.com/products/solutions/deployments).
2. Delete your deployment.

![Delete deployment](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-deployment.png)

That's it! You have successfully deleted the scraper, and you will not incur any disk or compute charges.

## How to Run a UI Scraper in a Virtual Machine

To run your scraper in a virtual machine, we will:
- Create a static IP
- Create a VM with that IP
- SSH into the VM
- Install the scraper

Now, follow these steps to run your scraper in a virtual machine:

1. Create a Google Cloud Account if you don't already have one.
   ![Select-your-billing-country](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/Select-your-billing-country.png)

2. Visit the [Google Cloud Console](https://console.cloud.google.com/welcome?cloudshell=true) and click the Cloud Shell button. A terminal will open up.
   ![click-cloud-shell-btn](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/click-cloud-shell-btn.png)

3. Run the following commands in the terminal:

   ```bash
   python -m pip install bota
   python -m bota create-ip
   ```

   You will be asked for a VM name. Enter any name you like, such as "pikachu".

   > Name: pikachu

   Then, you will be asked for the region for the scraper. Press Enter to go with the default, which is "us-central1", as it has the lowest-cost VMs.

   > Region: Default

   ![Install bota](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-bota.gif)

    With this a static IP address will be created for your VM, which you can use to access your app later.
    
4. Go to [Google Click to Deploy](https://console.cloud.google.com/marketplace/product/click-to-deploy-images/nodejs), create a deployment and configure it as follows or as appropriate based on your workload:
   ```
   Zone: us-central1-a # Use the zone from the region you selected in the previous step.
   Series: N1
   Machine Type: n1-standard-2 (2 vCPU, 1 core, 7.5 GB memory)
   Boot Disk Type: Standard persistent disk	# This is the most cost-effective disk option.
   Boot disk size in GB: 20 GB # Adjust based on storage needs  
   Network Interface [External IP]: pikachu-ip # Use the IP name you created in the previous step.
   ```
   ![deploy-node](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/deploy-node.gif)

5. Navigate to [VM Instances](https://console.cloud.google.com/compute/instances) and click the SSH button to SSH into the VM.
   ![ssh-vm](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/ssh-vm.png)

6.  Now, run the following command in the terminal:

   ```bash
   curl -sL https://raw.githubusercontent.com/omkarcloud/botasaurus/master/vm-scripts/install-bota.sh | bash
   ```

7. Finally, install the UI scraper by running the following command, then wait for 5 minutes for it to complete:
   ```bash
   python3 -m bota install-ui-scraper --repo-url https://github.com/omkarcloud/botasaurus-starter
   ```
   
   ![install-scraper](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-scraper.gif)
   Note: If you are using a different repo, replace `https://github.com/omkarcloud/botasaurus-starter` with your repo URL.

That's it! You have successfully launched the scraper in a virtual machine. When the previous commands are done, you will see a **link** to your scraper. Visit it to run your scraper.

![vm-success](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/vm-success.gif)

*Notes*
    - Update your project's `requirements.txt` to ensure it has all the dependencies required to run the scraper.
    - Ensure your VM has enough memory for your scraper's needs.
    - If running a headful browser, enable a virtual display by setting `enable_xvfb_virtual_display=True`. This creates a virtual display required for running a headful browser in a VM.
  ```python
  @browser(enable_xvfb_virtual_display=True)
  ```
    - The UI scraper will run indefinitely and will be available at the printed link.
    - If your UI scraper fails, you can check the logs of the current boot by running:
  ```bash
  journalctl -u backend.service -b 
  ```

##  How to Delete the UI Scraper and Avoid Incurring Further Charges

If you no longer need the scraper, please ensure you have downloaded your data before deleting it.

Next, follow these steps to delete the scraper:

1. Delete the static IP by running the following command:

   ```bash
   python -m bota delete-ip
   ```

   You will be asked for the name of the VM you created in the first step. Enter the name and press Enter.

   ![Delete IP](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-ip.png)

   Note: If you forgot the name of the IP, you can also delete all the IPs by running `python -m bota delete-all-ips`.

2. Go to [Deployments](https://console.cloud.google.com/products/solutions/deployments) and delete your deployment.

   ![Delete deployment](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/delete-deployment.png)

That's it! You have successfully deleted the scraper, and you will not incur any further charges.

### How to Run Scraper in Kubernetes?
Visit [this link](https://github.com/omkarcloud/botasaurus/blob/master/run-scraper-in-kubernetes.md) to learn how to run scraper at scale using Kubernetes.


### I have a feature request!

We'd love to hear it! Share them on [GitHub Discussions](https://github.com/omkarcloud/botasaurus/discussions). 

[![Make](https://raw.githubusercontent.com/omkarcloud/google-maps-scraper/master/screenshots/ask-on-github.png)](https://www.omkar.cloud/l/botasaurus-make-discussions/)
<!-- 
### Do you have a Discord community?

Yes, we have a Discord community where you can connect with other developers, ask questions, and share your experiences. Join our Discord community [here](https://discord.com/invite/rw9VeyuSM8). -->

### ❓ Advanced Questions

Congratulations on completing the Botasaurus Documentation! Now, you have all the knowledge needed to effectively use Botasaurus. 

You may choose to read the following questions based on your interests:

1. [How to Run Botasaurus in Google Colab?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-to-run-botasaurus-in-google-colab)

2. [How can I allow users to filter the scraped data?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-can-i-allow-users-to-filter-the-scraped-data)

3. [How can I allow the user to sort the scraped data?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-can-i-allow-the-user-to-sort-the-scraped-data)

4. [How can I present the scraped data in different views?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-can-i-present-the-scraped-data-in-different-views)

5. [When building a large dataset, customers often request data in different formats like overview and review. How can I do that?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#when-building-a-large-dataset-customers-often-request-data-in-different-formats-like-overview-and-review-how-can-i-do-that)

6. [What more can I configure when adding a scraper?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#what-more-can-i-configure-when-adding-a-scraper)

7. [How to control the maximum number of browsers and requests running at any point of time?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-to-control-the-maximum-number-of-browsers-and-requests-running-at-any-point-of-time)

8. [How do I change the title, header title, and description of the scraper?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-do-i-change-the-title-header-title-and-description-of-the-scraper)

9. [How can I use a database like PostgreSQL with UI Scraper?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-can-i-use-a-database-like-postgresql-with-ui-scraper)

10. [Which PostgreSQL provider should I choose among Supabase, Google Cloud SQL, Heroku, and Amazon RDS?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#which-postgresql-provider-should-i-choose-among-supabase-google-cloud-sql-heroku-and-amazon-rds)

11. [How to create a PostgreSQL database on Supabase?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-to-create-a-postgresql-database-on-supabase)

12. [How to create a PostgreSQL database on Google Cloud?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#how-to-create-a-postgresql-database-on-google-cloud)

13. [I am a Youtuber, Should I create YouTube videos about Botasaurus? If so, how can you help me?](https://github.com/omkarcloud/botasaurus/blob/master/advanced.md#i-am-a-youtuber-should-i-create-youtube-videos-about-botasaurus-if-so-how-can-you-help-me)

## Thank You
- To That, who has given me a sufficiently intelligent mind to create Botasaurus and do a lot of good.
- I made Botasaurus because I would be really happy if you could use it to successfully complete your project. So, a Gigantic Thank you for using Botasaurus!
- A heartfelt thank you to [Cheng Zhao](https://zcbenz.com/) from GitHub for creating Electron, which powers Botasaurus Desktop.
- Kudos to the Apify Team for creating the `proxy-chain` library. The implementation of SSL-based Proxy Authentication wouldn't have been possible without their groundbreaking work on `proxy-chain`.
- Shout out to [ultrafunkamsterdam](https://github.com/ultrafunkamsterdam) for creating `nodriver`, which inspired the creation of Botasaurus Driver.
- A big thank you to [daijro](https://github.com/daijro) for creating [hrequest](https://github.com/daijro/hrequests), which inspired the creation of botasaurus-requests.
- Deepest gratitude to [Flori Batusha](https://github.com/riflosnake) and [Ambri](https://github.com/iLeaf30/) for their contributions in creating **Botasaurus Humancursor**, which brings human-like mouse movements to Botasaurus.
- A humongous thank you to Cloudflare, DataDome, Imperva, and all bot recognition systems. Had you not been there, we wouldn't be either 😅.

*Now, what are you waiting for? 🤔 Go and make something mastastic! 🚀*

## Love It? [Star It! ⭐](https://github.com/omkarcloud/botasaurus)

Become one of our amazing stargazers by giving us a star ⭐ on GitHub!

It's just one click, but it means the world to me.

<a href="https://github.com/omkarcloud/botasaurus/stargazers">
    <img src="https://bytecrank.com/nastyox/reporoster/php/stargazersSVG.php?user=omkarcloud&repo=botasaurus" alt="Stargazers for @omkarcloud/botasaurus">
</a>


## Disclaimer for Botasaurus Project

> By using Botasaurus, you agree to comply with all applicable local and international laws related to data scraping, copyright, and privacy. The developers of Botasaurus are not responsible for any misuse of this software. It is the sole responsibility of the user to ensure adherence to all relevant laws regarding data scraping, copyright, and privacy, and to use Botasaurus in an ethical and legal manner.

We take the concerns of the Botasaurus Project very seriously. For any inquiries or issues, please contact Chetan Jain at [chetan@omkar.cloud](mailto:chetan@omkar.cloud). We will take prompt and necessary action in response to your emails.

