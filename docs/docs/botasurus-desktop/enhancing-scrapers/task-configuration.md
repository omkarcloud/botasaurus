---
sidebar_position: 11
---
# Task Configuration

**Task Configuration** lets you customize how tasks are displayed and processed.

You can:  
- Control task naming  
- Split large tasks into smaller ones  
- Combine results from multiple tasks into one task
- Remove duplicates from task results  

## Configuration Options

There are 4 options available for task configuration:

- `getTaskName` - Customize how tasks are named
- `splitTask` - Split a single input into multiple, smaller tasks
- `createAllTask` - Combine results from all split tasks into a single "All" task
- `removeDuplicates` - Remove duplicates from task results

Let's explore each option in detail.

## Custom Task Naming

By default, tasks on the `Tasks` page are named using their task ID, which makes it difficult to identify what data each task contains.

![Default task naming showing generic task IDs](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/task-name.png)

You can use `getTaskName` to generate meaningful task names based on input data. For example, you could name a task after the stock symbol it processes.

**How to Use It?**

Provide a function to `getTaskName` that receives the input `data` and returns a string.

```ts title="src/scraper/backend/server.ts"
import { Server } from "botasaurus-server/server"
import { stockPriceScraper } from "../src/scraper"

// Function to generate custom task name
function getTaskName(data) {
    return `${data.stock_symbol}`;
}

Server.addScraper(stockPriceScraper, {
    getTaskName: getTaskName
});
```

**Result:**
![Custom task names showing meaningful descriptions](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/get_task_name-result.png)

## Task Splitting

When scraping multiple items (like 200 URLs or 50 stock symbols), you may want to track each item separately. The `splitTask` option creates individual tasks for each item.

For example, if your input accepts multiple stock symbols, you can split them into separate tasks.
![Input form with multiple stock symbols](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/multi-urls.png)

**How to Use It?**

Provide a function to `splitTask` that receives the input `data` and returns an array of items. Botasaurus will create a new task for each item in the returned array.

```ts title="src/scraper/backend/server.ts"
import { Server } from "botasaurus-server/server"
import { stockPriceScraper } from "../src/scraper"

// Function to split input data into multiple tasks
function splitTask({stock_symbols, ...otherControlSettings}) {
    return stock_symbols.map(symbol => ({ stock_symbol: symbol, ...otherControlSettings }));
}

Server.addScraper(stockPriceScraper, {
    splitTask: splitTask
});
```

**Result:**
![Multiple tasks created from split operation](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/multi-task-spitted.png)

## Creating an "All Task"

When tasks are split, users often need to view all results in one place. Setting `createAllTask: true` automatically generates a combined view of all split task results, improving usability.

```ts title="src/scraper/backend/server.ts"
import { Server } from "botasaurus-server/server"
import { stockPriceScraper } from "../src/scraper"

function splitTask(data) {
    ...
}

Server.addScraper(
    stockPriceScraper,
    {
        splitTask: splitTask,
        createAllTask: true // Add this line
    }
);
```

**Result:**
![Tasks view showing individual tasks plus an "All Task" with combined results](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/create_all_task.png)

## Removing Duplicate Tasks

If your scraper produces duplicate items in its results, use the `removeDuplicatesBy` option to automatically filter out duplicates based on a specific field.

**How to Use It?**

Set `removeDuplicatesBy` to the field that uniquely identifies an item. 

For example, if each item has a unique `link`, you can remove duplicates like this:
```ts title="src/scraper/backend/server.ts"
Server.addScraper(searchResultsScraper, {
  splitTask: splitTask,
  createAllTask: true,
  removeDuplicatesBy: 'link' // Deduplicates based on this field  
});
```

This ensures that only one result item per unique `link` is kept.

**Notes on Deduplication:**
When using `removeDuplicatesBy` with `splitTask` and `createAllTask`, deduplication occurs in two stages:
1. **Within each task:** Duplicates are removed from each split task's results as it completes.
2. **In "All Task":** After all split tasks finish, their results are aggregated. Deduplication is then applied to this combined dataset, removing any duplicates that exist across different split tasks.

Due to this second stage, you may notice the total count in the "All Task" drop after the final split task completes.