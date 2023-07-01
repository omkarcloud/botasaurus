---
sidebar_position: 40
---

# Pausing Execution

This example shows how to pause execution in the driver, which can be useful for debugging purposes:

```python 
from bose import *

class Task(BaseTask):
    def run(self, driver, data):
        driver.prompt()
```