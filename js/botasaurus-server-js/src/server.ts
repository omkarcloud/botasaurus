import { BaseSort, Sort } from './sorts';
import { ScraperType } from './scraper-type';
import { isObject } from './utils';
import { _hash } from 'botasaurus/cache';
import * as fs from 'fs';
import { isNotNullish } from './null-utils'
import { kebabCase, capitalCase as titleCase } from 'change-case';
import { BaseFilter } from './filters'
import { View } from './views'
import { electronConfig, getInputFilePath, getReadmePath } from './paths'
import { createControls, FileTypes } from 'botasaurus-controls'

export function createEmailUrl({ email, subject, body }:any) {
  const emailSubject = encodeURIComponent(subject)
  const emailBody = encodeURIComponent(body)
  const emailURL = `mailto:${email}?subject=${emailSubject}&body=${emailBody}`
  return emailURL
}

function getReadme(): string {
  try {
    const readmeFile = getReadmePath();
    
    const text = fs.readFileSync(readmeFile, 'utf-8');
    return text;
  } catch (error) {
    // @ts-ignore
    if (error.code === 'ENOENT') {
      return '';
    }
    throw error;
  }
}

export function getScraperErrorMessage(validScraperNames: string[], scraperName: string | null, validNamesString: string) {
  if (validScraperNames.length === 0) {
      return `The scraper named '${scraperName}' does not exist. No scrapers are currently available. Please add a scraper using the Server.addScraper method.`
  }
  return validScraperNames.length === 1
      ? `A scraper with the name '${scraperName}' does not exist. The scraper_name must be ${validNamesString}.`
      : `A scraper with the name '${scraperName}' does not exist. The scraper_name must be one of ${validNamesString}.`
}



type WhatsAppSupportOptions = {
  number: string; // 10-digit phone number (without country code)
  countryCallingCode: string; // Country calling code (e.g., 81 for Japan, 1 for the US)
  message: string; // Default message for WhatsApp
};

/**
 * Replaces FileTypes constants (e.g., FileTypes.IMAGE) in a string of code
 * with their corresponding JSON array values.
 *
 * @param {string} code - The JavaScript/TypeScript code as a string.
 * @returns {string} - The modified code with FileTypes replaced, or the original code if no replacements are needed.
 */
function replaceFileTypesInCode(code: string): string {
  // 1. Gatekeeper: If the code doesn't mention 'FileTypes', do nothing.
  // This is a quick exit for efficiency.
  
  code = code.replace(
    /(const|let|var)\s*\{\s*FileTypes\s*\}\s*=\s*require\s*\(\s*['"`]botasaurus-controls['"`]\s*\)\s*;?/g,
    ""
  );
  if (!code.includes('FileTypes')) {
    return code;
  }

  let modifiedCode = code;

  // 2. Iterate over each key in our FileTypes object (e.g., "IMAGE", "EXCEL").
  for (const key of Object.keys(FileTypes)) {
    // TypeScript needs this assertion to know 'key' is a valid key of FileTypes
    const value = FileTypes[key as keyof typeof FileTypes];
    
    // Convert the array to its JSON string representation.
    // e.g., for 'IMAGE', this becomes "['jpeg','jpg','png',...]"
    const replacementString = JSON.stringify(value);

    // 3. Create robust regular expressions to find all occurrences.
    // We create two regexes to handle both common ways of accessing object properties.

    // Regex for dot notation: FileTypes.IMAGE
    // \b is a word boundary to prevent matching something like "MyFileTypes.IMAGE"
    const dotNotationRegex = new RegExp(`\\bFileTypes\\.${key}\\b`, 'g');
    
    // Regex for bracket notation: FileTypes['IMAGE'], FileTypes["IMAGE"], FileTypes[`IMAGE`]
    // It handles optional whitespace around the brackets and quotes.
    const bracketNotationRegex = new RegExp(`\\bFileTypes\\[\\s*['"\`]${key}['"\`]\\s*\\]`, 'g');

    // 4. Perform the replacements.
    modifiedCode = modifiedCode.replace(dotNotationRegex, replacementString);
    modifiedCode = modifiedCode.replace(bracketNotationRegex, replacementString);
  }

  return modifiedCode;
}

type EmailSupportOptions = {
  email: string; // Support email address
  subject: string; // Default email subject
  body: string; // Default email body
};

type Scraper = {
  name: string;
  function: Function;
  scraper_name: string;
  scraper_type: "browser" | "request" | "task";
  route_path: string
  get_task_name?: Function;
  create_all_task: boolean;
  split_task?: Function;
  filters: BaseFilter[];
  sorts: BaseSort[];
  views: View[];
  default_sort: string;
  remove_duplicates_by: string | null;
  isGoogleChromeRequired: boolean;
};
class _Server {
  scrapers: Record<string, Scraper> = {};
  private rateLimit: { browser?: number; request?: number; task?: number } | Record<string, number> = { browser: 1 };
  private controlsCache: Record<string, any> = {};
  public cache = false;
  private config: Record<string, any> | null = null;
  public isScraperBasedRateLimit: boolean = false;
  public whatsAppSupport: WhatsAppSupportOptions | null = null;
  public emailSupport: EmailSupportOptions | null = null;
  private scraperToInputJs: Record<string, Function> = {};

  getConfig(): Record<string, any> {
    if (!this.config) {
      if (electronConfig.productName === 'Todo My App Name') {
      this.config = {
        header_title: 'Botasaurus',
        right_header: {
          text: 'Love It? Star It! ★',
          link: 'https://github.com/omkarcloud/botasaurus',
        },
        readme: getReadme(),
      };  
      }else {
        this.config = {
        header_title: electronConfig.productName,
        right_header: this.emailSupport ? {
          text: 'Need Help? Mail Us!',
          link: createEmailUrl(this.emailSupport),
        } : {
          text: '',
          link: '',
        },
        readme: getReadme(),
      };  
      }
      
    }
    this.config.enable_cache = this.cache
    return this.config;
  }

  configure(
  {  
    headerTitle = '',
    rightHeader = {"text": "", "link": ""},
    readme = '',}:{
      headerTitle?: string;
      rightHeader?: { text?: string; link?: string };
      readme?: string;
    } 
  ): void {
    if (!isObject(rightHeader)) {
      throw new Error('rightHeader must be an object');
    }

    const validKeys = ['text', 'link'];
    if (!Object.keys(rightHeader).every((key) => validKeys.includes(key))) {
      throw new Error("rightHeader can only contain 'text' and 'link' keys");
    }

    if (!readme || readme.trim() === '') {
      readme = getReadme();
    }

    this.config = {
      "header_title":headerTitle,
      "right_header":rightHeader,
      "readme":readme,
    };
  }

  addWhatsAppSupport(options: WhatsAppSupportOptions) {
    if (options.number.length !== 10) {
      throw new Error('The WhatsApp number must be exactly 10 characters long.');
    }
    
    if (options.countryCallingCode.length < 1) {
      throw new Error('The country calling code must be at least 1 character long.');
    }

    if (options.countryCallingCode.includes('+')) {
      throw new Error('The country calling code must not contain a plus sign (+).');
    }
    this.whatsAppSupport = options;
  }

  addEmailSupport(options: EmailSupportOptions) {
    this.emailSupport = options;
  }

  setScraperToInputJs(scraperToInputJs: Record<string, Function>): void {
    this.scraperToInputJs = scraperToInputJs;
  }

  getControls(scraperName: string): any {
    this.updateCache(scraperName);
    return this.controlsCache[scraperName].controls;
  }

  updateCache(scraperName: string): void {

    if (
      !(scraperName in this.controlsCache)
    ) {
      this.controlsCache[scraperName] = {
        controls: createControls(this.scraperToInputJs[scraperName]),
      };
    }
  }

  addScraper(
    scraper:Function, {
      productName = null,
      getTaskName,
      createAllTask = false,
      splitTask,
      filters = [],
      sorts = [],
      views = [],
      removeDuplicatesBy = null,
      isGoogleChromeRequired
  }: {
    productName?: string | null;
    getTaskName?: Function;
    createAllTask?: boolean;
    splitTask?: Function;
    filters?: BaseFilter[];
    sorts?: BaseSort[];
    views?: View[];
    removeDuplicatesBy?: string | null;
    isGoogleChromeRequired?: boolean;
  } = {}
  ): void {
    // @ts-ignore
    if (scraper._isQueue) {
        throw new Error('The function is a queue function. Kindly use a browser, request, or task scraping function')
    }

    if (!scraper.hasOwnProperty('_scraperType')) {
      throw new Error('The function must be a browser, request, or task scraping function.');
    }

    // @ts-ignore
    if (scraper._scraperType !== ScraperType.REQUEST &&scraper._scraperType !== ScraperType.BROWSER &&scraper._scraperType !== ScraperType.TASK
    ) {
      // @ts-ignore
      throw new Error(`Invalid scraper type: ${scraper._scraperType}. Must be 'browser', 'request' or 'task'.`,);
    }

    if (createAllTask && typeof splitTask !== 'function') {
      throw new Error('splitTask function must be provided when createAllTask is true.');
    }

    if (!Array.isArray(filters)) {
      filters = [filters];
    }

    if (!Array.isArray(sorts)) {
      sorts = [sorts];
    }

    if (!Array.isArray(views)) {
      views = [views];
    }

    const viewIds = views.map((view) => view.id);
    if (viewIds.length !== new Set(viewIds).size) {
      const duplicateViewIds = viewIds.filter((id, index) => viewIds.indexOf(id) !== index);
      throw new Error(`Duplicate views found: ${duplicateViewIds}`);
    }

    const sortIds = sorts.map((sort) => sort.id);
    if (sortIds.length !== new Set(sortIds).size) {
      const duplicateSortIds = sortIds.filter((id, index) => sortIds.indexOf(id) !== index);
      throw new Error(`Duplicate sorts found: ${duplicateSortIds}`);
    }

    let isDefaultFound = false;
    let defaultSort: string | null = null;

    const noSort = new Sort('No Sort', []);
    noSort.id = 'no_sort';

    for (const sort of sorts) {
      if (sort.id === noSort.id) {
        throw new Error(`Sort id '${noSort.id}' is reserved. Kindly use a different id.`);
      }

      if (sort.isDefault) {
        if (isDefaultFound) {
          const nid = sort.id;
          throw new Error(
            `More than one default sort (${defaultSort}, ${nid}) found. Kindly apply isDefault sort on 1 Sort.`,
          );
        }
        isDefaultFound = true;
        defaultSort = sort.id;
      }
    }

    defaultSort =isNotNullish(defaultSort) ? defaultSort : noSort.id;
    noSort.isDefault = defaultSort === noSort.id;
    sorts.unshift(noSort);

    const filterIds = filters.map((filter) => filter.id);
    if (filterIds.length !== new Set(filterIds).size) {
      const duplicateFilterIds = filterIds.filter((id, index) => filterIds.indexOf(id) !== index);
      throw new Error(`Duplicate filters found: ${duplicateFilterIds}`);
    }
    // @ts-ignore
    const scraperFunctionName = scraper.__name__;
    if (['tasks', 'ui'].includes(scraperFunctionName.toLowerCase())) {
      throw new Error(`The scraper name '${scraperFunctionName}' is reserved. Please change the Scraper Name.`);
    }
    productName = isNotNullish(productName) ? productName : titleCase(scraperFunctionName);

    // @ts-ignore
    const scraper_type = scraper._scraperType
    this.scrapers[scraperFunctionName] = {
      name: productName as any,
      function: scraper,
      scraper_name: scraperFunctionName,
      scraper_type: scraper_type,
      route_path: kebabCase(scraperFunctionName),
      get_task_name: getTaskName,
      create_all_task: createAllTask,
      split_task: splitTask,
      filters,
      sorts,
      views,
      default_sort: defaultSort as any,
      remove_duplicates_by: removeDuplicatesBy,
      isGoogleChromeRequired: isGoogleChromeRequired || (scraper_type === ScraperType.BROWSER)
    };
  }

  getScrapersConfig(): any[] {
    const scraperList: any[] = [];

    for (const [scraperName, scraper] of Object.entries(this.scrapers)) {
      const inputJs = this.getInputJs(scraperName);
      const inputJsHash = _hash(inputJs);

      const viewsJson = scraper.views.map((view: any) => view.toJson());
      const defaultSort = scraper.default_sort;

      scraperList.push({
        name: scraper.name,
        scraper_name: scraperName,
        route_path:scraper.route_path, 
        input_js: inputJs,
        input_js_hash: inputJsHash,
        filters: scraper.filters.map((filter: any) => filter.toJson()),
        sorts: scraper.sorts.map((sort: any) => sort.toJson()),
        views: viewsJson,
        default_sort: defaultSort,
        max_runs: this.getMaxRuns(scraper),
      });
    }

    return scraperList;
  }

  getInputJs(scraperName: string): string {
    const inputJsPath = getInputFilePath(scraperName) 
    let inputJs: string | null = null;

    if (fs.existsSync(inputJsPath)) {
      inputJs = replaceFileTypesInCode(fs.readFileSync(inputJsPath, 'utf-8'));
    } else {
      const scraperFilePath = getInputFilePath(scraperName) 
      throw new Error(`Input js file not found for ${scraperName}, at path ${scraperFilePath}. Kindly create it.`);
    }

    return inputJs;
  }

  getScrapingFunction(scraperName: string): Function {
    return this.scrapers[scraperName].function;
  }

  getRemoveDuplicatesBy(scraperName: string): string | null {
    return this.scrapers[scraperName].remove_duplicates_by;
  }

  getScrapersNames(): string[] {
    return Object.keys(this.scrapers);
  }

  getScraper(scraperName: string): any {
    return this.scrapers[scraperName];
  }

  getBrowserScrapers(): string[] {
    return Object.entries(this.scrapers)
      .filter(([_, scraper]) => scraper.scraper_type === ScraperType.BROWSER)
      .map(([name]) => name);
  }

  getTaskScrapers(): string[] {
    return Object.entries(this.scrapers)
      .filter(([_, scraper]) => scraper.scraper_type === ScraperType.TASK)
      .map(([name]) => name);
  }

  getRequestScrapers(): string[] {
    return Object.entries(this.scrapers)
      .filter(([_, scraper]) => scraper.scraper_type === ScraperType.REQUEST)
      .map(([name]) => name);
  }

  private getMaxRuns(scraper: any): any{
    if (this.isScraperBasedRateLimit) {
      // For scraper-based rate limit, use the scraper name as key.
      // @ts-ignore
      return this.rateLimit[scraper.scraper_name] ?? null;
    } else {
      // For type-based rate limit, use the scraper type as key.
      // @ts-ignore
      return this.rateLimit[scraper.scraper_type] ?? null;
    }
  }

  setRateLimit(rateLimit: { browser?: number; request?: number; task?: number } | Record<string, number> = { browser: 1 }): void {
    const allowedKeys = ['browser', 'request', 'task'];
    const keys = Object.keys(rateLimit);
  
    // Case 1: Empty object — it's scraper based
    if (keys.length === 0) {
      this.isScraperBasedRateLimit = true;
      this.rateLimit = {};
      return;
    }
  
    const allValid = keys.every((key) => allowedKeys.includes(key));
  
    // Case 2: All valid keys — scraperType-based
    if (allValid) {
      this.isScraperBasedRateLimit = false;
      this.rateLimit = {
        browser: rateLimit.browser,
        request: rateLimit.request,
        task: rateLimit.task 
      };
      return;
    }
  
    // Case 3: Mixed valid + invalid — error
    if (!allValid && keys.some((key) => allowedKeys.includes(key))) {
      throw new Error(
        `Rate limit object must not mix scraper names with 'browser', 'request', or 'task'. Found keys: ${keys.join(', ')}`
      );
    }
  
    // Case 4: All invalid keys — scraper based
    this.isScraperBasedRateLimit = true;
    this.rateLimit = rateLimit;
  }
  
  validateRateLimit(): void {
    if (this.isScraperBasedRateLimit) {
      const scraperNames = new Set(this.getScrapersNames());
      const invalidKeys = Object.keys(this.rateLimit).filter(
        (key) => !scraperNames.has(key)
      );

      if (invalidKeys.length > 0) {
        const invalidKeysMessage = invalidKeys.length === 1 
          ? `Scraper with name '${invalidKeys[0]}' does not exist.` 
          : `Scrapers with names ${invalidKeys.join(', ')} do not exist.`;

        const formattedLimit = JSON.stringify(this.rateLimit).replaceAll(",", ", ").replaceAll(":", ": ");

        
        throw new Error(
          `Your rate limit is set to ${formattedLimit}, but ${invalidKeysMessage}`
        );
      }
    }
  }
  getRateLimit(): { browser?: number; request?: number; task?: number } | Record<string, number> {
    return this.rateLimit;
  }

  enableCache(): void {
    this.cache = true;
  }

  createTasks({ scraperName, data, metadata }: {
    scraperName: string;
    data: any;
    metadata: any;
  }): [any[], boolean, boolean] {
    const scraper = this.scrapers[scraperName];

    const tasks: any[] = [];

    const createAllTasks = scraper.create_all_task;
    const splitTask = scraper.split_task;

    if (splitTask) {
      const splitData = splitTask(data);
      for (const item of splitData) {
        const taskName = scraper.get_task_name ? scraper.get_task_name(item) : 'Unnamed Task';
        tasks.push({ name: taskName, data: item, metadata });
      }
    } else {
      const taskName = scraper.get_task_name ? scraper.get_task_name(data) : 'Unnamed Task';
      tasks.push({ name: taskName, data, metadata });
    }

    return [tasks, !!splitTask, createAllTasks];
  }

  getFilters(scraperName: string): BaseFilter[] {
    return this.scrapers[scraperName].filters;
  }

  getSorts(scraperName: string): BaseSort[] {
    return this.scrapers[scraperName].sorts;
  }

  getViews(scraperName: string): View[] {
    return this.scrapers[scraperName].views;
  }

  getDefaultSort(scraperName: string): string {
    return this.scrapers[scraperName].default_sort;
  }

  getSortIds(scraperName: string): string[] {
    return this.getSorts(scraperName).map((s) => s.id);
  }

  getViewIds(scraperName: string): string[] {
    return this.getViews(scraperName).map((v) => v.id);
  }
}

export const Server = new _Server();