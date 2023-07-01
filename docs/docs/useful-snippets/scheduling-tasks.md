---
sidebar_position: 80
---

# Scheduling Tasks

To introduce delays in the execution and create a more human-like behavior for the bot, you can utilize the scheduling capabilities provided by the ScheduleUtils class. 

Here's an example:


```python 
from bose import *

class Task(BaseTask):

    def schedule(self, data):
        """
            5 second delay between each task run.
        """
        return ScheduleUtils.delay_5s(data)
```