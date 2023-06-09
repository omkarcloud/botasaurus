---
sidebar_position: 10
---
# Google Maps Scraper

![Google Maps Scraper CSV Result](./img/gmap_result.png)

This is a Python script that allows you to scrape information from Google Maps, including business names, addresses, phone numbers, websites, ratings, and reviews. The script can be configured to search for specific queries and can scrape either the first page of results or all pages of results.

## Installation

1. Clone Starter Template
```
git clone https://github.com/omkarcloud/google-maps-scraper
cd google-maps-scraper
```
2. Install dependencies
```
python -m pip install -r requirements.txt
```
3. Run Project
```
python main.py
```

The script will start running and output progress updates to the console. When the scraper is complete, it will generate a CSV file named `finished.csv` in the `output` directory. The CSV file will contain the business name, address, phone number, website, rating, and review for each result.

Additionaly, you don't have to configure the Selenium driver as it will automatically download the appropriate driver based on your Chrome browser version.

## Configuration

- To specify the Google search queries to be used in the scraper, open the `src/scraper.py` file in your preferred text editor and update the `Task.queries` list with your desired queries.

- To specify whether to scrape the first page of Google Maps results or all pages of results, open the `src/scraper.py` file and set the `Task.GET_FIRST_PAGE` variable to `True` or `False` as appropriate.

![Google Maps Scraper CSV Result](./img/gmap_result.png)
