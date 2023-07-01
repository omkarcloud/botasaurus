---
sidebar_position: 65
---

# Closing Browser Automatically when Crashed

The following example demonstrates how to configure the browser to close itself automatically in the event of a crash:

```python 
class Task(BaseTask):
    task_config = TaskConfig(
        close_on_crash=True,
    )
```
