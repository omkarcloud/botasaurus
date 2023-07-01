---
sidebar_position: 80
---

# ScheduleUtils

ScheduleUtils allows you to introduce delays between Task Runs.

The following example demonstrates how to utilize ScheduleUtils to insert 5-second delays between 3 Task Runs.


```python
from bose import *

class Task(BaseTask):

    def schedule(self, data):
        return ScheduleUtils.delay_5s(data) # <---------------- 

    def get_data(self):
        return [1, 2, 3]

    def run(self, driver, account):
        pass
```


<!-- 
TODO: Maybe add more methods like this
Utilities to shecedule dealys between tasks 

Method

    delay(tasks, from, [to])
        gives random delat from to to.
        if to not given then delay of from is given 

    delay_5s(tasks)
        
    delay_30s_to_60s(tasks)

    delay_30m_to_60m(tasks)

 -->
 

