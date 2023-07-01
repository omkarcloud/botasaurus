---
sidebar_position: 60
---

# Random Sleeps

The following example demonstrates how to incorporate random sleep durations, which adds a more human-like behavior to the bot:

```python 
from bose import *

class Task(BaseTask):
    def run(self, driver, data):
        
        driver.short_random_sleep()
        
        driver.long_random_sleep()
```