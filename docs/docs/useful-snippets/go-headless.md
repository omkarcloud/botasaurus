---
sidebar_position: 10
---

# Go Headless

The following example demonstrates how to make the bot run headlessly:


```python 
class Task(BaseTask):
    browser_config = BrowserConfig(
        headless = True,
    )
```
