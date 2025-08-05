---
sidebar_position: 1
---

# Stock Price Scraper

This first extractor shows the "Playwright way" of scraping: open a browser, navigate to a page, grab a value, and return the data.

Creating this extractor is a simple 3-step process:

**1. Write a Playwright scraper function**  
**2. Add the function to the server**  
**3. Create a simple text input for the user interface**

Follow along and you'll have a desktop app fetching real-time stock prices in under 10 minutes.

### Step 1: Create the Scraper Function

Open `src/scraper/src/scraper.ts` and replace all its contents with the code below. This creates our `stockPriceScraper` function that will:

1. Receive a stock symbol from user input
2. Build the Yahoo Finance URL for that specific stock
3. Navigate to the page using Playwright
4. Extract the current stock price from this specific element:
![Highlighted Yahoo Finance Element](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/yahoo-finance-element.png)  
5. Return the data

```ts title="src/scraper/src/scraper.ts"
import { playwright } from 'botasaurus/playwright';

/**
 * Grabs the live quote for a given stock symbol from Yahoo Finance.
 */
const stockPriceScraper = playwright({
  // 👇 MUST match the input file name we'll create in Step 3
  // highlight-next-line
  name: 'stockPriceScraper',    
  headless: false,              // Show the browser window while scraping
  reuseDriver: true,            // Reuse the same browser instance for multiple tasks
  run: async ({ data, page }) => {
    // Extract the stock symbol from user input
    const stock_symbol = data['stock_symbol'];
    // Build the Yahoo Finance URL
    const link = `https://finance.yahoo.com/quote/${stock_symbol}`;

    // Navigate to the Yahoo Finance page
    await page.goto(link, { waitUntil: 'domcontentloaded' });

    // Extract the stock price using a selector
    const stock_price = parseFloat(
      (await page.textContent('[data-testid="qsp-price"]')) as string,
    );

    // Return the data
    return {
      stock_symbol: stock_symbol,
      stock_price: stock_price,
    };
  },
});

export { stockPriceScraper };
```

Have you noticed we named our scraper `stockPriceScraper`? 

This name is crucial—Botasaurus uses it to connect the scraper with its input controls js file, which we'll create in Step 3.

### Step 2: Add the Scraper

Now let's connect our scraper function to the desktop app. Open `src/scraper/backend/server.ts` and replace all its contents with the code below:

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';
import { stockPriceScraper } from '../src/stockPriceScraper';

// highlight-next-line
Server.addScraper(stockPriceScraper);
```

This single line connects your scraper with the desktop app, making it available in the user interface.

### Step 3: Create the Input Controls

Finally, let's create the user interface. Create a new file named `stockPriceScraper.js` in the `inputs` folder:

```js title="inputs/stockPriceScraper.js"
/**
 * @typedef {import('botasaurus-controls').Controls} Controls // 👈 Enables Code autocomplete
 */

/**
 * Renders the form users see on the Home page.
 * @param {Controls} controls
 */
function getInput(controls) {
  // highlight-start
  controls.text("stock_symbol", {
    label: "Stock Symbol",
    placeholder: "e.g. AAPL",
    defaultValue: "AAPL",
    isRequired: true,
    validate: (value) => {
      const errors = [];
      if (value.length !== 4) {
        errors.push("Length must be 4 characters");
      }
      if (!/^[A-Z]+$/.test(value)) {
        errors.push("Only uppercase letters allowed");
      }
      return errors;
    },
  });
  // highlight-end
}
```

This code creates a text input field where users can enter stock symbols. 

Also, the JSDoc comments enable code completion in VSCode, helping you discover all available input controls.

![Screenshot of stock symbol input field with AAPL as default](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-input-controls.png)

### 🎉 You're Done!

Congratulations! You've just built a fully functional **Stock Price Scraper** that runs as a desktop application.

**To test it:**

1. Press `Ctrl/⌘ + R` to reload the app  
2. Type any stock symbol (or use the default "AAPL") and click **Run**  
3. Watch as Chrome opens Yahoo Finance and navigates to your stock  
4. Click on the app window to see your results in a table format  

![Stock Scraper Demo extracting the AAPL quote](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/stock-scraper-preview.gif)


The next section will show you how to build an Amazon Invoice extractor that can save accountants hours of manual work.