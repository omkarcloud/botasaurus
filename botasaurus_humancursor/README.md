# Botasaurus Humancursor

A fork of [HumanCursor](https://github.com/riflosnake/HumanCursor) which brings human-like mouse movements to Botasaurus.

## Description

Botasaurus Humancursor is a Python library that enables human-like mouse movements in Botasaurus. It's designed to help you create more natural and less detectable web automation by simulating human-like cursor movements, clicks, and interactions.

This library is a fork of the original HumanCursor project, adapted to work with the Botasaurus driver instead of Selenium.

## Features

- Designed specifically to `bypass security measures and bot detection software`.
- Human-like mouse movements using Bezier curves
- Randomized movement patterns to avoid detection
- Support for clicking, dragging, and scrolling with human-like behavior

## Installation

```bash
pip install botasaurus-humancursor
```

## Usage

### Basic Example

# TODO: Add example
```python
from botasaurus_driver import Driver
from botasaurus_humancursor import WebCursor

# Initialize the Botasaurus driver
driver = Driver(headless=False)

# Navigate to a website
driver.get("https://www.example.com")

# Initialize HumanCursor
cursor = WebCursor(driver)

# Find an element
button = driver.select("button.login")

# Move to the element and click it with human-like movement
cursor.click_on(button)

# Close the driver
driver.close()
```

## Thank You  

- **Kudos to [Flori Batusha](https://github.com/riflosnake)** for creating [HumanCursor](https://github.com/riflosnake/HumanCursor). Building HumanCursor requires PhD-level mathematical expertise, and Flori's brilliance shines through in this remarkable project.  
- **Deepest Gratitude to [Ambri](https://github.com/iLeaf30/)** for creating a fork of HumanCursor specifically tailored for Botasaurus.

## License

This project is licensed under the MIT License