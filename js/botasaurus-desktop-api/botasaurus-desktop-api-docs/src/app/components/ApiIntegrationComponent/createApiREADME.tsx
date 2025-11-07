import { hasViews, hasFilters, hasSorts } from '../../utils/models'

const defaultIndentation = 4
function jsObjectToJsObjectString(object: any, indent: number = defaultIndentation, bracketsIndentation: number = 0): string {
  const x = ' '.repeat(indent)
  const bracketsIndentationStr = ' '.repeat(bracketsIndentation)

  const entriesList = Object.entries(object)
  if (entriesList.length === 0) {
    return bracketsIndentationStr + '{}'
  }

  const entries = entriesList.map(([key, value]) => {
    // Handle different value types
    if (typeof value === 'string') {
      return `${x}${key}: '${value}',` // Strings need quotes
    } else if (Array.isArray(value)) {
      if (value.length > 0 && typeof value[0] === 'string') {
        const z = value.map((v) => `'${v}'`).join(', ') // Strings in arrays need quotes
        const y = `[${z}]`
        return `${x}${key}: ${y},` // Arrays use JSON.stringify
      } else {
        return `${x}${key}: ${JSON.stringify(value)},` // Arrays use JSON.stringify
      }
    } else if (value === null) {
      return `${x}${key}: null,` // Null becomes null
    } else if (typeof value === 'boolean') {
      return `${x}${key}: ${value},` // Booleans stay as true/false
    } else {
      return `${x}${key}: ${value},` // Numbers and other values directly
    }
  })

  // Construct the final JavaScript object string with indentation
  const formattedString = `${bracketsIndentationStr}{\n` + entries.join('\n') + `\n${bracketsIndentationStr}}`
  return formattedString
}
function createCanBeOneOptionsString(options: any[]): string {
  const sliceLength = 10
  if (options.length === 0) {
    return "// No options available"
  } else if (options.length > sliceLength) {
    return `// Can be one among ${options.length} options: ${(options.slice(0, sliceLength).map((option) => option.value)).join(', ')}, ...`
  } else {
    return `// Can be one of the following options: ${joinStrings(options.map((option) => option.value))}`
  }
}
function createCanBeAnyOptionsString(options: any[]): string {
  const sliceLength = 10

  if (options.length === 0) {
    return "// No options available"
  } else if (options.length > sliceLength) {
    return `// Can be any among ${options.length} options: ${(options.slice(0, sliceLength).map((option) => option.value)).join(', ')}, ...`
  } else {
    return `// Can be any combination of the following options: ${joinStrings(options.map((option) => option.value))}`
  }
}
function filtersToJsObjectString(filters: any[], indent: number = defaultIndentation, bracketsIndentation: number = 0): string {
  const x = ' '.repeat(indent) + "// "
  const bracketsIndentationStr = ' '.repeat(bracketsIndentation)
  if (filters.length === 0) {
    return `{} // No filters available`
  }
  const entries = filters.map(({ id, type, options }) => {
    switch (type) {
      case 'MinNumberInput':
      case 'MaxNumberInput':
        return `${x}${id}: 0, // Enter a number`
      case 'IsTrueCheckbox':
      case 'IsFalseCheckbox':
      case 'IsNullCheckbox':
      case 'IsNotNullCheckbox':
      case 'IsTruthyCheckbox':
      case 'IsFalsyCheckbox':
        return `${x}${id}: true, // Must be true only`
      case 'BoolSelectDropdown':
      case 'SingleSelectDropdown':
        return `${x}${id}: 'your-option', ${createCanBeOneOptionsString(options)}`
      case 'MultiSelectDropdown':
        return `${x}${id}: ['your-option-1', 'your-option-2'], ${createCanBeAnyOptionsString(options)}`
      case 'SearchTextInput':
        return `${x}${id}: '', // Enter your search text string`
      default:
        throw Error('Not Implemented')
    }
  })

  // Construct the final JavaScript object string with indentation
  const formattedString = `{\n` + entries.join('\n') + `\n${bracketsIndentationStr}}`
  return formattedString
}

function createCachingText(enable_cache: boolean): string {
  if (enable_cache) {
    return `## Caching

The API automatically **caches** results to minimize redundant scraping. This means:
- Scraper results are stored based on input data
- Subsequent requests with the same input data return cached data instantly

### Changing Cache Settings

You can change this caching behavior when initializing the API client:

\`\`\`typescript
// Option 1: Disable caching for fresh results
const api = new Api({ enableCache: false })

// Option 2: Keep caching enabled (default)
const api = new Api({ enableCache: true })
\`\`\``;
  } else {
    return `## Caching

The API does not **cache results**, so you get fresh results on every request.

### Changing Cache Settings

You can change this caching behavior when initializing the API client:

\`\`\`typescript
// Option 1: Enable caching to improve performance
const api = new Api({ enableCache: true })

// Option 2: Keep caching disabled for fresh results (default)
const api = new Api({ enableCache: false })
\`\`\`

When caching is enabled:
- Scraper results are stored based on input data
- Subsequent requests with the same input data return cached data instantly`;
  }
  
}

function createApiTaskText(scraperName: string, hasSingleScraper: boolean, defaultData: any, maxRunsMessage): string {
  const x = hasSingleScraper ? '' : `scraperName: '${scraperName}', `

  return `To create an asynchronous task, use the \`createAsyncTask\` method:

\`\`\`javascript
const data = ${jsObjectToJsObjectString(defaultData)}
const asyncTask = await api.createAsyncTask({ ${x}data })
\`\`\`

To create a synchronous task, use the \`createSyncTask\` method:

\`\`\`javascript
const syncTask = await api.createSyncTask({ ${x}data })

\`\`\`

You can create multiple asynchronous or synchronous tasks at once using the \`createAsyncTasks\` and \`createSyncTasks\` methods, respectively:

\`\`\`javascript
const dataItems = [
${jsObjectToJsObjectString(defaultData, 8, 4)},
${jsObjectToJsObjectString(defaultData, 8, 4)},
]
const asyncTasks = await api.createAsyncTasks({ ${x}dataItems })
const syncTasks = await api.createSyncTasks({ ${x}dataItems })
\`\`\`

Also, ${maxRunsMessage}
`
}
function createScraperTaskDataText(scraperName: string, hasSingleScraper: boolean): string {
  const x = hasSingleScraper ? '' : `, scraperName: '${scraperName}'`
  return `{ data${x} }`
}
function createScraperTaskDataText2(scraperName: string, hasSingleScraper: boolean): string {
  const x = hasSingleScraper ? '' : `, scraperName: '${scraperName}'`
  return `{ dataItems${x} }`
}
function createFilterString(filters: any[]): string {
  return `\n filters: ${filtersToJsObjectString(filters, 8, 4)}`
}
function joinStrings(strings: string[], separator: string = 'or'): string {
  if (strings.length === 0) {
    return ""
  } else if (strings.length === 1) {
    return strings[0]
  } else {
    const lastElement = strings.pop()
    const joinedStrings = strings.join(", ")
    return `${joinedStrings} ${separator} ${lastElement}`
  }
}

function humaniseRoutes(final: string[]) {
  return joinStrings(final.map(item => `\`${item}\``))
}

function createSortString(sorts: any[], defaultSort: string): string {
  return `\n sort: null, // sort can be one of: ${joinStrings(sorts.map((view) => {
    if (view.id === defaultSort) {
      return `${view.id} (default)`
    }
    return view.id
  }))}`
}
function createViewsString(views: any[]): string {
  if (views.length === 1) {
    return `\n view: null, // view can be ${views[0].id}`
  } else {
    return `\n view: null, // view can be one of: ${joinStrings(views.map((view) => view.id))}`
  }
}
function generateList(pagination: boolean, views: any, filters: any, sorts: any): string[] {
  const result: string[] = []

  if (pagination) {
    result.push("pagination")
  }
  if (hasViews(views)) {
    result.push("views")
  }

  if (hasFilters(filters)) {
    result.push("filters")
  }

  if (hasSorts(sorts)) {
    result.push("sorts")
  }

  return result
}
function createFetchingTaskResultsText(sorts: any[], filters: any[], views: any[], defaultSort: string): string {
  const ls = joinStrings(generateList(true, views, filters, sorts), "or")

  return `You can also apply ${ls} to task results:

\`\`\`javascript
const results = await api.getTaskResults({
  taskId: 1,
  page: 1,
  perPage: 3,${hasViews(views) ? createViewsString(views) : ""}${hasSorts(sorts) ? createSortString(sorts, defaultSort) : ""}${hasFilters(filters) ? createFilterString(filters) : ""}
})
\`\`\``
}
function createFetchingTaskText(sorts: any[], filters: any[], views: any[], defaultSort: string): string {
  return `By default, all tasks are returned. You can also apply pagination:

\`\`\`javascript
const results = await api.getTasks({
  page: 1,
  perPage: 3,
})
\`\`\``
}
function createDownloadTaskText(sorts: any[], filters: any[], views: any[], defaultSort: string): string {
  const ls = joinStrings(generateList(false, views, filters, sorts), "or")
  if (ls) {
    return `To download the results of a specific task in a particular file format, use the \`downloadTaskResults\` method:

\`\`\`javascript
import fs from 'fs'

const { buffer, filename } = await api.downloadTaskResults({
  taskId: 1,
  format: 'csv',
})

fs.writeFileSync(filename, buffer)
\`\`\`

You can also apply ${ls}:

\`\`\`javascript
import fs from 'fs'

const { buffer, filename } = await api.downloadTaskResults({
  taskId: 1,
  format: 'csv',
})

fs.writeFileSync(filename, buffer)
\`\`\``
  } else {
    return `To download the results of a specific task in a particular file format, use the \`downloadTaskResults\` method:

\`\`\`javascript
import fs from 'fs'

const { buffer, filename } = await api.downloadTaskResults({
  taskId: 1,
  format: 'csv',
})

fs.writeFileSync(filename, buffer)
\`\`\``
  }
}

function makeAPI(baseUrl, apiBasePath) {
  const config: string[] = []

  if (baseUrl) {
    config.push(`apiUrl: '${baseUrl}'`)
  }

  if (apiBasePath) {
    config.push(`apiBasePath: '${apiBasePath}'`)
  }
  
  config.push(`createResponseFiles: true`)


  return config.length > 0 ? `const api = new Api({ ${config.join(', ')} })` : 'const api = new Api()'
}
export function createApiREADME(
  baseUrl: string,
  scraperName: string,
  hasSingleScraper: boolean,
  defaultData: any,
  sorts: any[],
  filters: any[],
  views: any[],
  defaultSort: string,
  route_path: string,
  max_runs: number | null,
  apiBasePath: string, 
  routeAliases:string[],
  enable_cache: boolean
): string {
  const maxRunsMessage = max_runs === null
    ? "This scraper supports unlimited concurrent tasks."
    : max_runs === 1
      ? "You can run only **1** task of this scraper concurrently."
      : `You can run up to **${max_runs}** tasks of this scraper concurrently.`;

  const maxRunsMessage2 = max_runs === null
    ? "Allow unlimited concurrent runs of this scraper."
    : max_runs === 1
      ? "Allow only **1** concurrent run of this scraper."
      : `Allow up to **${max_runs}** concurrent runs of this scraper.`;

  const route_path_cleaned = `/${route_path}`
  const final = routeAliases.concat([route_path_cleaned])

  const humanFinal = humaniseRoutes(final)

  return `# API Integration

The Botasaurus API client provides a convenient way to access the ${hasSingleScraper ? 'Scrapers' : 'Scraper'} via an API.

It provides a simple and convenient way to create, fetch, download, abort, and delete tasks, as well as manage their results.

## Installation

To use the Botasaurus API client, first install the package using the following command:

\`\`\`bash
npm install botasaurus-desktop-api

\`\`\`

## Usage

First, import the \`Api\` class from the library:

\`\`\`javascript
import Api from 'botasaurus-desktop-api'

\`\`\`
Then, create an instance of the \`Api\` class:

\`\`\`javascript
async function main() {
  ${makeAPI(baseUrl, apiBasePath)}
}

main()
\`\`\`

Additionally, the API client will create response JSON files in the \`output/responses/\` directory to help with debugging and development.

In production, remove the \`createResponseFiles: true\` parameter.

### Creating Tasks

There are two types of tasks:
- Asynchronous Task
- Synchronous Task

Asynchronous tasks run asynchronously, without waiting for the task to be completed. The server will return a response immediately, containing information about the task, but not the actual results. The client can then retrieve the results later.

Synchronous tasks, on the other hand, wait for the completion of the task. The server response will contain the results of the task.

You should use asynchronous tasks when you want to run a task in the background and retrieve the results later. Synchronous tasks are better suited for scenarios where you have a small number of tasks and want to wait and get the results immediately.

${createApiTaskText(scraperName, hasSingleScraper, defaultData, maxRunsMessage)}

### Fetching Tasks

To fetch tasks from the server, use the \`getTasks\` method:

\`\`\`javascript
const tasks = await api.getTasks()

\`\`\`

${createFetchingTaskText(sorts, filters, views, defaultSort)}

To fetch a specific task by its ID, use the \`getTask\` method:

\`\`\`javascript
const task = await api.getTask(1)

\`\`\`

### Fetching Task Results Only

To fetch only the results of a specific task, use the \`getTaskResults\` method:

\`\`\`javascript
const results = await api.getTaskResults({ taskId: 1 })

\`\`\`

${createFetchingTaskResultsText(sorts, filters, views, defaultSort)}

### Downloading Task Results

${createDownloadTaskText(sorts, filters, views, defaultSort)}

### Aborting and Deleting Tasks

To abort a specific task, use the \`abortTask\` method:

\`\`\`javascript
await api.abortTask(1)

\`\`\`

To delete a specific task, use the \`deleteTask\` method:

\`\`\`javascript
await api.deleteTask(1)

\`\`\`

You can also bulk abort or delete multiple tasks at once using the \`abortTasks\` and \`deleteTasks\` methods, respectively:

\`\`\`javascript
await api.abortTasks({ taskIds: [1, 2, 3] })
await api.deleteTasks({ taskIds: [4, 5, 6] })
\`\`\`

## Direct Call (Bypassing Task System)

If you prefer a lightweight, immediate way to run the scraper without the overhead of creating, scheduling, and running tasks, you can make a direct \`GET\` request to the ${humanFinal} endpoint.


\`\`\`javascript
const result = await api.get('${final[0]}', ${jsObjectToJsObjectString(defaultData)})

\`\`\`
This will:
- Make a **GET** request to the \`${final[0]}\` endpoint.
- Execute the scraper immediately, bypassing task creation, scheduling, and running overhead.
- Validate input data before execution, returning a \`400\` error for invalid requests.
${enable_cache ? '- Cache the results based on the provided input data.\n' : ''}- ${maxRunsMessage2}

This method is especially useful when:

- You simply want to call the scraper and get the result, without the task management overhead.
- You plan to resell the API via platforms like **RapidAPI**, where the task abstraction is unnecessary.

## Examples

Here are some example usages of the API client:

\`\`\`javascript
import fs from 'fs'
import Api from 'botasaurus-desktop-api'

async function main() {
  // Create an instance of the API client
  ${makeAPI(baseUrl, apiBasePath)}

  // Create a synchronous task
  const data = ${jsObjectToJsObjectString(defaultData, defaultIndentation, 2)}
  const task = await api.createSyncTask(${createScraperTaskDataText(scraperName, hasSingleScraper)})

  // Fetch the task
  const fetchedTask = await api.getTask(task.id)

  // Fetch the task results
  const results = await api.getTaskResults({ taskId: task.id })

  // Download the task results as a CSV
  const { buffer, filename } = await api.downloadTaskResults({ 
    taskId: task.id, 
    format: 'csv' 
  })
  fs.writeFileSync(filename, buffer)

  // Abort the task
  await api.abortTask(task.id)

  // Delete the task
  await api.deleteTask(task.id)

  // --- Bulk Operations ---

  // Create multiple synchronous tasks
  const dataItems = [
    ${jsObjectToJsObjectString(defaultData, 8, 4)},
    ${jsObjectToJsObjectString(defaultData, 8, 4)},
  ]
  const tasks = await api.createSyncTasks(${createScraperTaskDataText2(scraperName, hasSingleScraper)})

  // Fetch all tasks
  const allTasks = await api.getTasks()

  // Bulk abort tasks
  await api.abortTasks({ taskIds: tasks.map(t => t.id) })

  // Bulk delete tasks
  await api.deleteTasks({ taskIds: tasks.map(t => t.id) })
}

main()
\`\`\`

${createCachingText(enable_cache)}

## That's It!

Now, go and build something awesome.`
}