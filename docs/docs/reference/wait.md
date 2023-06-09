---
sidebar_position: 50
---
# Wait

The Wait provides a set of commonly used pre-defined waits useful in web scraping.

Class Attributes
----------------

- `SHORT` Integer literal that represents 4 seconds
- `LONG` Integer literal that represents 8 seconds
- `VERY_LONG` Integer literal that represents 16 seconds

Usage
-----

Wait is commonly used when selecting elements. 

For example the following example specifies to wait 4 seconds to find divs with class "quote".

```python
from bose import BaseTask, Wait

class Task(BaseTask):

    def run(self, driver):
        # ... Amazing Code 
        els = driver.get_elements_or_none_by_selector('div.quote', Wait.SHORT)
```
