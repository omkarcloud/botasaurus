---
sidebar_position: 17
---

# Rate Limiting

Rate limiting controls how many scrapers can run simultaneously. This helps prevent system overload and reduces the risk of getting blocked.

You can set rate limits in two ways:
- By the scraper's name (recommended)  
- By the scraper's type (browser or task)

## By Scraper Name (Recommended)

This is the preferred method for controlling scraper execution. It allows you to set specific limits for individual scrapers by name.

For example, to allow:
- 1 concurrent instance of `stockPriceScraper`  
- 40 concurrent instances of `amazonPdfExtractor`

Use this configuration:

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';

Server.setRateLimit({ 
  stockPriceScraper: 1, 
  amazonPdfExtractor: 40,
});
```

## By Scraper Type

Alternatively, you can set limits based on the scraper type:

- `browser`: Limits concurrent Playwright scrapers
- `task`: Limits concurrent Task scrapers

For example, to allow:
- 1 concurrent browser scraper  
- 40 concurrent task scrapers  

Use this configuration:

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';

Server.setRateLimit({ 
  browser: 1, 
  task: 40,
});
```

## Default Behavior

If you don't set any rate limits, Botasaurus applies these defaults:
- **Browser scrapers:** 1 at a time
- **Task scrapers:** Unlimited

This default configuration prevents accidental resource overload from running too many browser instances simultaneously.