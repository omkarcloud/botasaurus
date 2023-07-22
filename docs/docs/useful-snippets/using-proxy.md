---
sidebar_position: 10
---

# Go Headless

The following example demonstrates how to use a proxy:

```python 
class Task(BaseTask):
    browser_config = BrowserConfig(
        proxy = "http://lum-customer-hl_1b230841-zone-MYZONE:MYPW@zproxy.lum-superproxy.io:22225"
    )
```
