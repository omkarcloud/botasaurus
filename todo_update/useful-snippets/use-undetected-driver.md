---
sidebar_position: 20
---

# Use Undetected Driver

The following example demonstrates how to make the bot use the Undetected Driver created by [Ultrafunkamsterdam](https://github.com/ultrafunkamsterdam):

```python 
class Task(BaseTask):
    browser_config = BrowserConfig(
        use_undetected_driver = True,
    )
```
