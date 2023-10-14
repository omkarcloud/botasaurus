---
sidebar_position: 2
---

# Getting Started

:::info Prerequisites

To use Botasaurus effectively, it is helpful to have a familiarity with Python and Selenium concepts.

:::

This section will guide you through the steps to create a new Botasaurus project using starter template, which is recommended for most Greenfield automation projects.

---

Clone Starter Template

```bash
git clone https://github.com/omkarcloud/botasaurus-starter my-botasaurus-project
```

Then change into `my-botasaurus-project` directory, install dependencies, open vscode, and start the project:

```bash
cd my-botasaurus-project
python -m pip install -r requirements.txt
code . # Optionally, open the project in VSCode
python main.py
```

<!-- Once started it will scrape google search for "botasaurus web scraping framework" keyword and store the results in `output/finished.json` -->
Once started it will scrape data and store the results in `output/finished.json`. 
<!-- ![Result](./img/google-scraping.png) -->

You can edit the `task.py` file based on your Project Needs. 

## Next Steps

If you are new to Botasaurus, we encourage you to learn about Botasaurus [here](sign-up-tutorial.md).