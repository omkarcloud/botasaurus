---
sidebar_position: 70
---

# No Beep Sound

The following example demonstrates prevent the bot from producing beep sounds when prompting:


```python 
class Task(BaseTask):
    task_config = TaskConfig(
        beep=False,
    )
```