---
sidebar_position: 5
---

# Scraper Types  

Botasaurus Desktop provides two types of scrapers to handle different extraction scenarios:

### Playwright Scrapers for Web Scraping

Playwright Scrapers launch a Chrome browser to scrape websites. It is a stealthier version of Playwright that's optimized for web scraping.

Use a Playwright scraper when you need to:

- Scrape JavaScript-heavy sites (React, Vue, Angular)
- Scroll through infinite lists or click buttons/forms
- Bypass bot-protection

**Example** 
```ts
import { playwright } from 'botasaurus/playwright';

export const webScraper = playwright({
  name: 'webScraper',
  headless: true,  // Set to false in production to hide the window
  run: async ({ page }) => {
    await page.goto('http://example.com');
    const h1 = await page.textContent('h1');
    return { h1 };
  }
})
```

### Task Scrapers for File Parsing & API Calls
Task scrapers run in pure Node.js with no browser overhead. They are ideal for operations that can be handled through network requests or file parsing.

Use a Task scraper when you need to:
- Extract data from PDFs or Excel files
- Call REST endpoints

**Example** 
```ts
import { task } from 'botasaurus/task';

export const taskScraper = task({
  name: 'taskScraper',
  run: ({ data }) => {
    // Return data as is
    return data;
  }
})
```

---

Use a **Playwright Scraper** if you need to open a website, and a **Task-Based Scraper** for everything else, like processing files or calling APIs.