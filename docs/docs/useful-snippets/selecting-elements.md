---
sidebar_position: 30
---

# Selecting element

The following example illustrates how to select elements using the Bose Driver methods:


```python 
# Select an element by Selector
el = driver.get_element_or_none_by_selector('form input[type="email"]', Wait.LONG)

# Select multiple elements by Selector
els = driver.get_elements_or_none_by_selector('form input[type="email"]', Wait.LONG)

# Select an element by XPATH
el = driver.get_element_or_none("//button[starts-with(@data-item-id,'phone')]")

# Select an element by ID
el = driver.get_element_by_id("your-id", wait=Wait.LONG)

# Select an element by Text
el = driver.get_element_or_none_by_text("Success", wait=Wait.LONG)

# Select an element by Text Contains (partial match)
el = driver.get_element_or_none_by_text_contains("Success", wait=Wait.LONG)

```
