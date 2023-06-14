---
sidebar_position: 60
---
# Opponent

The Opponent class represents anti-bot services like Cloudflare or PerimeterX.

It's commonly used to determine which captcha service detected the bot usually in conjunction with the `BoseDriver.get_bot_detected_by` method.

```python
from bose import BaseTask, Opponent

class Task(BaseTask):

    def run(self, driver):
        # ... Amazing Code 
        detected_by = driver.get_bot_detected_by()
        if detected_by == Opponent.CLOUDFLARE:
            print('Detected by ', Opponent.CLOUDFLARE)
        elif detected_by == Opponent.PERIMETER_X:
            print('Detected by ', Opponent.PERIMETER_X)

```

If the bot was detected by Cloudflare, the message "Bot detected by Cloudflare" is printed to the console. If the bot was detected by PerimeterX, the message "Bot detected by PerimeterX" is printed instead.
