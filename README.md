# Bose - The Ultimate Web Scraping Framework!

बोस वेब स्क्रैपिंग फ्रेमवर्क सुभाष चंद्र बोस को समर्पित है।

—

Omkar’s Bose Web Scraping Framework is Django for Web Scraping. It is battery packed framework which helps ypu scrape websites faster by providing you with utilities  to help you scraper and debugging easier. 

Some of Best feautres of Bose Scraping Framework which will help you are: 

- Pre built Web Scraping Solutions for Google Maps, G2 etc. So you don’t need to do any work at all.
- Automatically Follows Best Practices to avoid Detection from Websites and Cloudflare
- User Agent Rotation.
- Logging of html, erros and screenshots to help you in debugging.
- Auto Retry on Failure Feautres
- Keeping track of time to run scraper
- Detection whether bot is caught by Cloudflare, PermiterX, DataDome etc.

Bose Scraping Framework needs improvement in following feautures

- Bypass of detection in PermiterX and DataDome by studying their bot detection algorithms.

---

## Installation

```
git clone https://github.com/omkarcloud/bose-starter web-scraper
cd web-scraper
python install.py
```

# Tutorial

Let’s say we want to scrape [g2.com](http://g2.com) products related to our enemies like Cloudflare. These are really bad guys that protects website from Scraping 😂. 

Specifically g2 uses cloudflare. so we need to defeat cloudflare and scrape g2 Products. 

two tyes of drivers, 

default driver

untedetced driver created by 

the default driver is fast to start but is generally detected by bot protrction sites like cloudflare whereas untedetced driver created by is slow to start but less likely to detect. So we will use undetected driver here. 

First, we will visit page “/”. Is is best practice in Web Scraping to visit websites using search engines [google.com](http://google.com) as thatv is how most humans visit. So let’s do a organic_get of “/”. 

driver.organic_get(”/”)

scrapes data. 

add random short sleep 3 to 7, or long sleep 8 to 12.

get next button utility. 

add random wait 

and click it. 

scraped it. 

save it to finished 

save as csv file 

Save Screenshots of

---

Save Screenshot 

Retry Feautre Explanation 

Success and Failure Folders etc explain 

# Api Reference

RetryException

you can raise this exception to retry the Bot automatically retry running the Bot

LocalStorage 

`localStorage.get_item(item)`

`localStorage.set_item(item, value)`

The value can not only be string but also dicts, or lists.  

`localStorage.remove_item(item)`

Deletes all items from `localStorage` 

`localStorage.clear()`

Output 

 pending = Output.read_pending()

 pending = Output.write_pending()

 

 finished = Output.read_finished()

 finished = Output.write_finished()

Output.save_as_csv(json_list, filename = ‘finished.csv’)

Output.save_as_xlsx(json_list, filename = ‘finished.xlsx’)

Output.save_as_json(json_list, filename = ‘finished.xlsx’)

BoseDriver

Bose Driver adds some useful methods to make selenium more helpful for scrapping 

**get_via_google()**

using it the browser visits [google.com](http://google.com) and visits url to make it more humane. 

**sleep(n)**

sleeps for n seconds 

**short_random_sleep()**

 sleeps randomly for 3 to 7 seconds. Use it for waiting on pages to make bot look more humane. 

**long_random_sleep()**

sleeps randomly for 7 to 12 seconds. Use it for waiting on pages to make bot look more humane. 

**is_bot_detected()**

check if the bot is **detected** by cloudflare or perimeterx and show human verification test. 

**sleep_forever()**

makes browser sleep forever. Useful for debugging. 

save_success_screenshot()

save_failure_screenshot()

scroll_element(element)

scroll_site

js_click() 

get_by_current_page_referrer()

get_element_by_id() // if id starts with # Remove it

get_cookies() 

get_local_storage() 

get_cookies_and_local_storage() 

add_cookies(data) 

add_local_storage(data) 

add_cookies_and_local_storage(data) 

delete_cookies() 

delete_local_storage() 

delete_cookies_and_local_storage() 

get_local_storage_api()

get_html() 

Task 

run(driver): 

called when the task is to be run 

Use 1920x3600 always 

change agent 

# How To

### Responsible Usage

The Bose Framework is made to help humanity. So please uphold dharma and don’t harm others for your own benefit.  

FAQs

Could you tell us more about bot protection bypassing. 

Sure

How do I change my IP to a Resendential IPs?

The best, simple and free way is as follows:  

in case you are using mobile data via hotspot, just switch on aeroplane mode and then switch off aeroplane mode. Turn on Hotspot if get’s off and you will get new IP.

// TODO Photo 

in case you are using wifi, just switch it off and switch it on and you will get new IP.

// TODO Photo 

Note that we commend using mobile data via hotspot as it is faster to change ip then turning off wifi router. 

Additionaly you may also consider buying proxies which 

which is expensive anf cost around $15 if using resedential ip

cost around $0.11 if using datacenter ip

Ideas: 

Allow to configure user agent and window size behaviour?

Add Selectors 

Add @wait_on_exception decorater to run_task?