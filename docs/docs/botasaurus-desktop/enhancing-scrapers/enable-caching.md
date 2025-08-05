---
sidebar_position: 5
---
# Enabling Caching

Caching saves the results of a scraper run. When you run the scraper again with the same inputs, Botasaurus serves the cached result instead of running the scraper again, saving both time and compute resources.

## How to Enable Caching

To enable caching for all scrapers, add `Server.enableCache()` to `src/scraper/backend/server.ts` file:

```ts title="src/scraper/backend/server.ts"
import { Server } from "botasaurus-server/server"

// highlight-next-line
Server.enableCache();
```

## How Caching Works

Botasaurus uses input data to determine whether to use a cached result:

1. When you run a scraper, Botasaurus creates a unique "cache key" from the `data` object
2. If the same `data` values are used in a future run, the cached result is returned instantly
3. If the `data` values change, the scraper runs again

**Example:** If you scrape a product page with `data: { productId: "123" }`, the result is cached. Running the scraper again with the same `productId` returns the cached result without re-running the scraper.

## Excluding Fields from the Cache Key

Some inputs should not affect caching decisions. For example:
- API keys
- Session cookies  
- Proxy URLs

These values may change between runs without affecting the scraper's results. Including them in the cache key would cause unnecessary re-runs.

To exclude these fields from caching, mark an input control with `isMetadata: true`:

```js
// In your inputs/myScraper.js
.text("api_key", {
   label: "API Key",
   // highlight-next-line
   isMetadata: true,
})
```

When `isMetadata` is set to `true`:
- The value moves from the `data` object to the `metadata` object
- Botasaurus excludes `metadata` when creating cache keys

You can access metadata values in your scraper like this:

```ts
const myScraper = task({
  name: "myScraper",
  run: ({ data, metadata }) => {
    // The api_key is now in metadata and won't affect caching
    // highlight-next-line
    const apiKey = metadata["api_key"];
    
    // ... your scraper logic
  }
})
```

This approach ensures that only essential, data-defining inputs determine caching behavior, making your cache more effective.

## Bypassing Cache Control

When caching is enabled, users see a **"Use cache"** checkbox in the input form:

![Cache Control](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/cache-control.png)

This checkbox:
   - Defaults to `true` (using cached results if available)
   - Allows users to bypass the cache for a specific run by unchecking it