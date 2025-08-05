---
sidebar_position: 9
---

# Custom Views

**Custom Views** display your data in multiple, easy-to-read tables in the `Results` page.

For example, if your scraper returns product data with nested reviews, you can create  
- An **"Overview"** table with key details like name and price
- A **"Reviews"** table that expands each review into its own row

This not only enhances readability but also allows users to export the data in structured format (CSV/JSON) by selecting the view.

![Export formatted data from a Custom View](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/export-example.png)

## Creating a Simple View
The code below adds a view called "Overview" that shows `name` and `price` fields.

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';
import { View, Field } from 'botasaurus-server/ui';
import { yourScraper } from '../src/yourScraper';   // your scraper function

/* 1. Define the view */
// highlight-start
const overviewView = new View('Overview', [
  new Field('name'),
  new Field('price'),
]);
// highlight-end
/* 2. Register scraper + view */
Server.addScraper(yourScraper, { views: [overviewView] });
```

How it works  
- `new View('Overview', …)` creates a tab called **Overview**  
- `new Field('name')` / `new Field('price')` creates columns  
- `Server.addScraper(…, { views: [overviewView]})` adds the `Overview` view to the scraper

![simple view](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/simple-view.png)

## Types of Fields

You can use **4** types of fields to build views.

### `Field`

Displays a single value from your data record. It's the most common field.

**Options**
- `outputKey` renames the column header, such as changing `price` to `product_price`
- `map` transforms the value using a function. Perfect for calculating an average, formatting a date, or adding a currency symbol
- `showIf` conditionally omits the column based on input form data

**Example**
```ts
new Field("reviews_per_rating", { 
    outputKey: "average_rating", 
    map: (value, record) => {
        // ... Logic to calculate average rating from the 'value' object
    }, 
    // Only show this column if the user checked "scrape_prices"
    showIf: (inputData) => inputData.scrape_prices === true 
})
```

### `CustomField`
Creates a new column from multiple values in the record.

*Supports `showIf` option only.*

**Example**
```ts
// Combines two fields into one
new CustomField("full_name", (record) => `${record.first_name} ${record.last_name}`
)
```

### `ExpandDictField`
Expands a single dictionary object into multiple columns.

*Supports `showIf` option only.*

**Example**
```ts
// Convert a rating like {1: 0, 2: 0, 3: 0, 4: 100, 5: 900} into 5 new columns
new ExpandDictField("reviews_per_rating",[
        new Field("1", { outputKey: "rating_1" }),
        new Field("2", { outputKey: "rating_2" }),
        new Field("3", { outputKey: "rating_3" }),
        new Field("4", { outputKey: "rating_4" }),
        new Field("5", { outputKey: "rating_5" }),
    ],
)
```

### `ExpandListField`
Expands an array of objects into multiple rows. Each item in the array becomes a new row. 

For example, if a product has 3 reviews, it creates 3 rows in the table.

*Supports `showIf` option only.*

**Example**
```ts
new ExpandListField('reviews', [
  new Field('rating'),
  new Field('content'),
])
```

## Real World Example 

Let's say a scraper returns the following product data.

```ts
const taskScraper = task({
  name: "taskScraper",
  run: () => {
    // highlight-start
    return [
      {
        id: 1,
        name: "T-Shirt",
        price: 16, // in US Dollar
        reviews: 1000,
        reviews_per_rating: {
          1: 0,
          2: 0,
          3: 0,
          4: 100,
          5: 900,
        },
        featured_reviews: [
          {
            id: 1,
            rating: 5,
            content: "Awesome t-shirt!",
          },
          {
            id: 2,
            rating: 5,
            content: "Amazing t-shirt!",
          },
        ],
      },
      {
        id: 2,
        name: "Laptop",
        price: 700,
        reviews: 500,
        reviews_per_rating: {
          1: 0,
          2: 0,
          3: 0,
          4: 100,
          5: 400,
        },
        featured_reviews: [
          {
            id: 1,
            rating: 5,
            content: "Best laptop ever!",
          },
          {
            id: 2,
            rating: 5,
            content: "Great laptop!",
          },
        ],
      },
    ];
    // highlight-end
  },
})
```

The following code creates **3** views from this data  
-  **"Overview"** shows a summary of each product with expanded rating data
    ![Overview view](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/overview.png)
-  **"Featured Reviews"** displays a detailed list where each review is its own row
    ![Reviews view](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/reviews.png)

```ts title="src/scraper/backend/server.ts"
import { Server } from 'botasaurus-server/server';
import { View, Field, ExpandDictField, ExpandListField, CustomField } from 'botasaurus-server/ui';
import { scrapeProductData } from '../src/scrapeProductData';   // <-- your scraper

/**
 * Calculate the average product-rating.
 *
 * @param value - The `reviews_per_rating` dictionary.
 * @param record - The entire product record.
 */
function calculateAverageRating(value: Record<string, number>): number {
  const totalReviews = Object.values(value || {}).reduce((a, b) => a + b, 0);
  if (totalReviews === 0) return 0;

  let ratingSum = 0;
  for (const [rating, count] of Object.entries(value)) {
    ratingSum += Number(rating) * count;
  }
  return parseFloat((ratingSum / totalReviews).toFixed(2));
}


// highlight-start
const overviewView = new View('Overview', [
  new Field('id'),
  new Field('name'),
  new Field('price'),
  new Field('reviews'),

  // Create a new column 'average_rating' by transforming 'reviews_per_rating'
  new Field('reviews_per_rating', {
    outputKey: 'average_rating',
    map: calculateAverageRating,
  }),

  // Expand the 'reviews_per_rating' dictionary into individual rating columns
  new ExpandDictField('reviews_per_rating', [
    new Field('1', { outputKey: 'rating_1' }),
    new Field('2', { outputKey: 'rating_2' }),
    new Field('3', { outputKey: 'rating_3' }),
    new Field('4', { outputKey: 'rating_4' }),
    new Field('5', { outputKey: 'rating_5' }),
  ]),
]);
// highlight-end

// highlight-start
const featuredReviewsView = new View('Featured Reviews', [
  // Alias parent data for clarity in the reviews table
  new Field('id',   { outputKey: 'product_id'   }),
  new Field('name', { outputKey: 'product_name' }),

  // Expand the list of featured reviews into separate rows
  new ExpandListField('featured_reviews', [
    new Field('rating'),
    new Field('content'),
  ]),
]);
// highlight-end

Server.addScraper(
  scrapeProductData,
  {
    views: [
      overviewView,
      featuredReviewsView,
    ],
  }
);
```
**Result**
![overview photo](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/overview.png)

:::info
An **`All Fields`** view is always included by default, showing all raw data returned by the scraper without any transformations.
:::


