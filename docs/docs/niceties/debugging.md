---
sidebar_position: 30
---

# Debugging

## Exception handling

Exceptions are common when using Selenium. In bare Selenium, if an exception occurs, the driver automatically closes, leaving you with only logs to debug.

In Bose, when an exception occurs in a scraping task, the browser remains open instead of immediately closing. This allows you to see the live browser state at the moment the exception occurred, which greatly helps in debugging.

![error prompt](/img/error-prompt.png)

## Debugging

Web scraping can often be fraught with errors, such as incorrect selectors or pages that fail to load. When debugging with raw Selenium, you may have to sift through logs to identify the issue. Fortunately, Bose makes it simple for you to debug by storing information about each run.

After each run a directory is created in tasks which contains three files, which are listed below:

### `task_info.json`
It contains information about the task run such as duration for which the task run, the ip details of task, the user agent, window_size and profile which used to execute the task. 

![task info](/img/task-info.png)

### `final.png`
This is the screenshot captured before driver was closed. 

![final](/img/final.png)


### `page.html`
This is the html source captured before driver was closed. Very useful to know in case your selectors failed to select elements.


![Page](/img/page.png)


### `error.log`
In case your task crashed due to exception we also store error.log which contains the error due to which the task crashed. This is very helful in debugging.

![error log](/img/error-log.png)
