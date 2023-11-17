### AntiDetectDriver: Making Web Scraping Simple

AntiDetectDriver is a modified version of Selenium designed to evade detection by bot protection services like Cloudflare. It includes numerous helper functions that simplify web scraping tasks.

#### Browser Features

**Typing into Input Fields**

- Use `.type` to enter text into input fields.
  ```python
  driver.type('input[type="email"]', email)
  ```

**Clicking Elements**

- `.click` simulates a mouse click on elements selected by CSS selectors.
  ```python
  driver.click(".button")
  ```

**Scrolling to Elements**

- `.scroll` scrolls the view to the element selected by CSS selectors.
  ```python
  driver.scroll(".scrollable-element")
  ```

**Extracting Text from Elements**

- `.text` retrieves the text content from the selected element.
  ```python
  driver.text('.content')
  ```

**Parsing the Page with BeautifulSoup**

- `.bs4` provides the current page source as a BeautifulSoup object.
  ```python
  soup = driver.bs4
  ```

**Finding Elements or Returning None**

- `get_element_or_none` functions find elements without throwing an exception if they don't exist.
  ```python
  element = driver.get_element_or_none("//div[@class='example']")
  element = driver.get_element_or_none_by_selector(".example-class")
  element = driver.get_element_or_none_by_text_contains("Example")
  ```

**Collecting Links**

- `.links` collects all hyperlinks that match the provided selector.
  ```python
  links = driver.links('a.post-link')
  ```

**Element Existence Check**

- `.exists` verifies the presence of an element on the page.
  ```python
  exists = driver.exists(".button")
  ```

#### Local Storage Manipulation

**Simplified Local Storage Interaction**

- Interact with the browser's local storage using the `local_storage` variable, which eliminates the need for `driver.execute_script`.
  ```python
  driver.local_storage.set_item('username', 'johndoe')
  username = driver.local_storage.get_item('username')
  driver.local_storage.remove_item('username')
  driver.local_storage.clear()
  ```

#### Page Navigation and Interaction

**Checking for Page Presence**

- `.is_in_page` checks if the current browser URL matches the specified path.
  ```python
  is_in_page = driver.is_in_page('/search', wait=8) # Optional wait
  ```

**Executing External JavaScript Files**

- `.execute_file` runs a JavaScript file located in the root project directory, facilitating the use of advanced editing tools.
  ```python
  driver.execute_file('make_red.js')
  ```

**Taking Screenshots**

- `.save_screenshot` captures the current webpage view and saves it to the output/ directory.
  ```python
  driver.save_screenshot()
  ```

#### Anti-Detection Features

**Organic Page Loading**

- `.organic_get` simulates a search engine referral, opening the Google homepage before navigating to the target URL.
  ```python
  driver.organic_get("https://www.omkar.cloud/auth/sign-up/")
  ```

**Referral-Based Navigation**

- `.get_by_current_page_referrer` navigates to a URL as if the user clicked a link on the current page, mimicking human-like browsing patterns.
  ```python
  driver.get_by_current_page_referrer("https://example.com")
  ```

**Randomized Sleep Intervals**

- `.short_random_sleep` introduces a random short delay between actions to mimic human timing.
  ```python
  driver.short_random_sleep()
  ```

**Detection Check**

- `.is_bot_detected` checks for common bot detection triggers activated by Cloudflare/PerimeterX.
  ```python
  is_detected = driver.is_bot_detected()
  ```
