from typing import List

from bs4 import BeautifulSoup
from datetime import datetime
from random import uniform
from time import sleep
from traceback import print_exc

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .output import is_slash_not_in_filename

from .decorators_utils import create_directory_if_not_exists
from .beep_utils import beep_input
from .local_storage_driver import LocalStorage
from .opponent import Opponent
from .utils import read_file, relative_path, sleep_for_n_seconds, sleep_forever
from .wait import Wait
from .driver_about import AboutBrowser
from .accept_google_cookies import accept_google_cookies


class AntiDetectDriver(webdriver.Chrome):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.about: AboutBrowser = None
        self.is_network_enabled = False
        self.close_proxy = False

    """
    Utility functions
    """
    def bs4(self) -> BeautifulSoup:
        """Returns a BeautifulSoup object for parsing HTML content."""
        return BeautifulSoup(self.page_source, 'html.parser')

    def prompt(self, text="Press Enter To Continue..."):
        """Displays a prompt with an optional text message and waits for user input."""
        return beep_input(text, self.about.beep if self.about else True)

    @staticmethod
    def sleep(n):
        """Pauses the execution for 'n' seconds."""
        sleep_for_n_seconds(n)

    @staticmethod
    def random_sleep(a: float, b: float):
        """Pauses the execution for a random duration between 'a' and 'b' seconds."""
        sleep_for_n_seconds(uniform(a, b))

    def save_screenshot(self, filename=datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".png"):
        """Takes a screenshot and saves it with the provided or default filename."""
        try:
            if not filename.endswith(".png"):
                filename = filename + ".png"

            if is_slash_not_in_filename(filename):
                create_directory_if_not_exists("output/screenshots/")
                filename = f'output/screenshots/{filename}'
            filename = relative_path(filename, 0)
            self.get_screenshot_as_file(filename)
        except:
            print_exc()
            print('Failed to save screenshot')

    def _enable_network(self) -> None:
        """Enables network functionality using Chrome DevTools Protocol (CDP)."""
        if not self.is_network_enabled:
            self.is_network_enabled = True
            self.execute_cdp_cmd('Network.enable', {})

    """
    Get URL Functions
    """

    def get_by_current_page_referrer(self, link, wait=None):
        """
        Navigates to the provided link and waits until the current URL changes.
        Args:
            link (str): The URL to navigate to.
            wait (float): Optional waiting time after navigation in seconds.
        """
        current_url = self.current_url
        self.execute_script(f'window.location.href = "{link}";')

        while current_url == self.current_url:
            sleep(0.1)

        sleep(wait) if wait and wait != 0 else None

    def get_by_google_referrer(self, link, wait=None, accept_cookies=False):
        """
        Navigates to Google's homepage, accepts cookies if specified, and then navigates to the provided link.
        Args:
            link (str): The URL to navigate to.
            wait (float): Optional waiting time after navigation in seconds.
            accept_cookies (bool): Flag to accept cookies on Google's homepage.
        Returns:
            None
        """
        self.get("https://www.google.com/")
        accept_google_cookies(self) if accept_cookies else None
        return self.get_by_current_page_referrer(link, wait)

    """
    Anti Bot Detection Functions
    """

    def get_bot_detected_by(self):
        """
        Detects the type of bot detection mechanism on the current page.
        Returns:
            str: The type of bot detection mechanism detected (PERIMETER_X, CLOUDFLARE), or None if no detection.
        """
        pmx = self.get_element_by_xpath("//*[text()='Please verify you are a human']", None)
        if pmx is not None:
            return Opponent.PERIMETER_X

        clf = self.get_element_by_selector("#challenge-running", None)
        if clf is not None:
            return Opponent.CLOUDFLARE

        return None

    def is_bot_detected(self):
        """
        Checks if the bot detection mechanism is detected on the current page.
        Returns:
            bool: True if bot detection is detected, False otherwise.
        """
        return self.get_bot_detected_by() is not None

    def prompt_to_solve_captcha(self, more_rules: list = None):
        """
        Displays a prompt to solve a captcha with optional additional rules.
        Args:
            more_rules (list): List of additional rules for solving the captcha.
        Returns:
            None
        """
        if more_rules is None:
            more_rules = []
        print('')
        print('   __ _ _ _    _                          _       _           ')
        print('  / _(_) | |  (_)                        | |     | |          ')
        print(' | |_ _| | |   _ _ __      ___ __ _ _ __ | |_ ___| |__   __ _ ')
        print(r' |  _| | | |  | | `_ \    / __/ _` | `_ \| __/ __| `_ \ / _` |')
        print(' | | | | | |  | | | | |  | (_| (_| | |_) | || (__| | | | (_| |')
        print(r' |_| |_|_|_|  |_|_| |_|   \___\__,_| .__/ \__\___|_| |_|\__,_|')
        print('                                   | |                        ')
        print('                                   |_|                        ')
        print('')

        return beep_input('Press fill in the captcha, the faster the less detectable, then press enter to continue ...',
                          self.about.beep)

    """
    Search for WebElements Functions
    """

    def get_element_by_xpath(self, xpath, wait=Wait.SHORT) -> WebElement | None:
        """
        Finds a single WebElement using XPath.
        Args:
            xpath (str): The XPath selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        try:
            return WebDriverWait(self, wait).until(EC.presence_of_element_located((By.XPATH, xpath))) if wait \
                else self.find_element(By.XPATH, xpath)
        except:
            return None

    def get_elements_by_xpath(self: WebDriver, xpath, wait=Wait.SHORT):
        """
        Finds multiple WebElements using XPath.
        Args:
            xpath (str): The XPath selector.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[WebElement] | None: List of located WebElements or None if not found.
        """
        try:
            if wait:
                WebDriverWait(self, wait).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return self.find_elements(By.XPATH, xpath)
        except:
            return None

    def get_element_by_selector(self, selector, wait=Wait.SHORT) -> WebElement | None:
        """
        Finds a single WebElement using CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the element to be clickable.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        try:
            return WebDriverWait(self, wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))) if wait \
                else self.find_element(By.CSS_SELECTOR, selector)
        except:
            return None

    def get_elements_by_selector(self: WebDriver, selector, wait=Wait.SHORT) -> List[WebElement] | None:
        """
        Finds multiple WebElements using CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[WebElement] | None: List of located WebElements or None if not found.
        """
        try:
            if wait:
                WebDriverWait(self, wait).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return self.find_elements(By.CSS_SELECTOR, selector)
        except:
            return None

    def get_element_by_id(self, _id: str, wait=Wait.SHORT) -> WebElement | None:
        """
        Finds a single WebElement using the element ID.
        Args:
            _id (str): The element ID.
            wait (float): Optional wait time for the element to be clickable.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        return self.get_element_by_selector(f'[id="{_id.lstrip("#")}"]', wait)

    def get_element_by_name(self, selector, wait=Wait.SHORT):
        """
        Finds a single WebElement using the element name.
        Args:
            selector (str): The element name.
            wait (float): Optional wait time for the element to be present.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        return WebDriverWait(self, wait).until(EC.presence_of_element_located((By.NAME, selector))) if wait \
            else self.find_element(By.NAME, selector)

    def get_element_by_text(self, text, wait=Wait.SHORT) -> WebElement | None:
        """
        Finds a single WebElement by matching the exact text.
        Args:
            text (str): The exact text to match.
            wait (float): Optional wait time for the element to be present.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        return self.get_element_by_xpath(f'//*[text()="{text}"]', wait)

    def get_element_by_text_contains(self, text, wait=Wait.SHORT) -> WebElement | None:
        """
        Finds a single WebElement by containing the specified text.
        Args:
            text (str): The partial text to match.
            wait (float): Optional wait time for the element to be present.
        Returns:
            WebElement | None: The located WebElement or None if not found.
        """
        return self.get_element_by_xpath(f'//*[contains(text(), "{text}")]', wait)

    def exists(self, selector: str, wait=Wait.SHORT) -> bool:
        """
        Checks if an element with the specified selector exists on the page.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            bool: True if the element exists, False otherwise.
        """
        return True if self.get_element_by_selector(selector, wait) else False

    def text(self, selector: str, wait=Wait.SHORT) -> str | None:
        """
        Retrieves the text content of the WebElement matched by the CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            str | None: The text content of the located WebElement or None if not found.
        """
        el = self.get_element_by_selector(selector, wait)
        return el.text if el else None

    def text_xpath(self, xpath: str, wait=Wait.SHORT) -> str | None:
        """
        Retrieves the text content of the WebElement matched by the XPath.
        Args:
            xpath (str): The XPath selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            str | None: The text content of the located WebElement or None if not found.
        """
        el = self.get_element_by_xpath(xpath, wait)
        return el.text if el else None

    def get_link_by_xpath(self, xpath: str, wait=Wait.SHORT) -> str | None:
        """
        Retrieves the href attribute of the link matched by the XPath.
        Args:
            xpath (str): The XPath selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            str | None: The href attribute of the located link or None if not found.
        """
        el = self.get_element_by_xpath(xpath, wait)
        return el.get_attribute("href") if el else None

    def get_link_by_selector(self, selector: str, wait=Wait.SHORT) -> str | None:
        """
        Retrieves the href attribute of the link matched by the CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            str | None: The href attribute of the located link or None if not found.
        """
        el = self.get_element_by_selector(selector, wait)
        return el.get_attribute("href") if el else None

    def get_links_by_xpath(self, selector: str, wait=Wait.SHORT) -> List[str] | None:
        """
        Retrieves a list of href attributes of links matched by the XPath.
        Args:
            selector (str): The XPath selector.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[str] | None: List of href attributes of located links or an empty list if not found.
        """
        els = self.get_elements_by_xpath(selector, wait)
        return [el.get_attribute("href") for el in els] if els else []

    def get_links_by_selector(self, selector: str, wait=Wait.SHORT) -> List[str] | None:
        """
        Retrieves a list of href attributes of links matched by the CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[str] | None: List of href attributes of located links or an empty list if not found.
        """
        els = self.get_elements_by_selector(selector, wait)
        return [el.get_attribute("href") for el in els] if els else []

    def get_links(self, search=None, wait=Wait.SHORT):
        """
        Retrieves a list of href attributes of all the links on the page.
        Args:
            search (str): Optional substring to filter links by.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[str]: List of href attributes of located links matching the search criteria.
        """
        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("href")

            return list(map(extract_link, elements))

        els = self.get_elements_by_selector("a", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search is None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))

    def get_images(self, search=None, wait=Wait.SHORT):
        """
        Retrieves a list of src attributes of all the images on the page.
        Args:
            search (str): Optional substring to filter images by.
            wait (float): Optional wait time for the elements to be present.
        Returns:
            List[str]: List of src attributes of located images matching the search criteria.
        """
        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("src")

            return list(map(extract_link, elements))

        els = self.get_elements_by_selector("img", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search is None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))

    @staticmethod
    def get_element_parent(element) -> WebElement:
        """
        Retrieves the parent element of the specified WebElement.
        Args:
            element (WebElement): The WebElement whose parent is to be retrieved.
        Returns:
            WebElement: The parent WebElement of the specified element.
        """
        return element.find_element(By.XPATH, "./..")

    @staticmethod
    def get_element_text(element):
        """
        Retrieves the inner text content of the specified WebElement.
        Args:
            element (WebElement): The WebElement whose inner text is to be retrieved.
        Returns:
            str: The inner text content of the WebElement.
        """
        return element.get_attribute('innerText')

    @staticmethod
    def get_innerhtml(element):
        """
        Retrieves the inner HTML content of the specified WebElement.
        Args:
            element (WebElement): The WebElement whose inner HTML is to be retrieved.
        Returns:
            str: The inner HTML content of the WebElement.
        """
        return element.get_attribute("innerHTML")

    """
    Interact with WebElements Functions
    """

    def scroll(self, selector: str, wait=Wait.SHORT):
        """
        Scrolls the page to bring the specified element into view.
        Args:
            selector (str): The CSS selector of the element to scroll to.
            wait (float): Optional wait time for the element to be present.
        Returns:
            bool: True if the element can be scrolled, False otherwise.
        Raises:
            NoSuchElementException: If the element with the specified selector is not found.
        """
        element = self.get_element_by_selector(selector, wait)
        if element is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False

    def scroll_site(self):
        """
        Scrolls the entire page by a fixed amount (10,000 pixels).
        """
        self.execute_script("""window.scrollBy(0, 10000);""")

    def can_element_be_scrolled(self, element):
        """
        Checks if the specified element can be scrolled.
        Args:
            element (WebElement): The WebElement to check.
        Returns:
            bool: True if the element can be scrolled, False otherwise.
        """
        # <=3 is a fix to handle floating point numbers
        result = not (self.execute_script(
            "return Math.abs(arguments[0].scrollTop - (arguments[0].scrollHeight - arguments[0].offsetHeight)) <= 3",
            element))
        return result

    def scroll_into_view(self, element):
        """
        Scrolls the page to bring the specified element into view.
        Args:
            element (WebElement): The WebElement to scroll into view.
        Returns:
            None
        """
        return self.execute_script("arguments[0].scrollIntoView()", element)

    def scroll_element(self, element):
        """
        Scrolls the page to bring the specified element into view.
        Args:
            element (WebElement): The WebElement to scroll to.
        Returns:
            bool: True if the element can be scrolled, False otherwise.
        """
        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False

    def js_click(self, element):
        """
        Performs a JavaScript click on the specified element.
        Args:
            element (WebElement): The WebElement to perform the click action.
        Returns:
            None
        """
        self.execute_script("arguments[0].click();", element)

    def click(self, selector, wait=Wait.SHORT):
        """
        Performs a JavaScript click on the element matched by the CSS selector.
        Args:
            selector (str): The CSS selector.
            wait (float): Optional wait time for the element to be present.
        Returns:
            None
        Raises:
            NoSuchElementException: If the element with the specified selector is not found.
        """
        el = self.get_element_by_selector(selector, wait)
        if el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        self.js_click(el)

    def type(self, selector: str, text: str, wait=Wait.SHORT):
        """
        Types the specified text into the input element matched by the CSS selector.
        Args:
            selector (str): The CSS selector.
            text (str): The text to type into the input element.
            wait (float): Optional wait time for the element to be present.
        Returns:
            None
        Raises:
            NoSuchElementException: If the input element with the specified selector is not found.
        """
        input_el = self.get_element_by_selector(selector, wait)
        if input_el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        input_el.send_keys(text)

    def type_and_confirm(self, selector: str, text: str, wait=Wait.SHORT):
        """
        Types the specified text into the input element matched by the CSS selector and confirms with ENTER.
        Args:
            selector (str): The CSS selector.
            text (str): The text to type into the input element.
            wait (float): Optional wait time for the element to be present.
        Returns:
            None
        Raises:
            NoSuchElementException: If the input element with the specified selector is not found.
        """
        input_el = self.get_element_by_selector(selector, wait)
        if input_el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        input_el.send_keys(text)
        input_el.send_keys(Keys.ENTER)

    """
    Cookie & Storage Functions
    """

    @property
    def local_storage(self):
        """
        Provides access to the LocalStorage functionality.
        Returns:
            LocalStorage: An instance of the LocalStorage class.
        """
        return LocalStorage(self)

    def get_local_storage_dict(self):
        """
        Retrieves the key-value pairs stored in the LocalStorage.
        Returns:
            dict: A dictionary containing the key-value pairs from the LocalStorage.
        """
        storage = LocalStorage(self)
        return storage.items()

    def add_local_storage_dict(self, local_storage):
        """
        Adds key-value pairs to the LocalStorage.
        Args:
            local_storage (dict): A dictionary containing the key-value pairs to be added.
        Returns:
            None
        """
        storage = LocalStorage(self)
        for key in local_storage:
            storage.set_item(key, local_storage[key])

    def delete_local_storage_dict(self):
        """
        Clears both LocalStorage and SessionStorage.
        Returns:
            None
        """
        self.execute_script("window.localStorage.clear();")
        self.execute_script("window.sessionStorage.clear();")

    def get_cookies_dict(self):
        """
        Retrieves the cookies as a dictionary.
        Returns:
            dict: A dictionary containing the cookies.
        """
        all_cookies = self.get_cookies()
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict

    def get_cookies_and_local_storage_dict(self):
        """
        Retrieves both cookies and LocalStorage as a dictionary.
        Returns:
            dict: A dictionary containing both cookies and LocalStorage key-value pairs.
        """
        cookies = self.get_cookies_dict()
        local_storage = self.get_local_storage_dict()

        return {"cookies": cookies, "local_storage": local_storage}

    def add_cookies_dict(self, cookies):
        """
        Adds cookies to the current browser session.
        Args:
            cookies (dict): A dictionary containing cookies to be added.
        Returns:
            None
        """
        for key in cookies:
            self.add_cookie({"name": key, "value": cookies[key]})

    def add_cookies_and_local_storage_dict(self, site_data):
        """
        Adds both cookies and LocalStorage key-value pairs to the current browser session.
        Args:
            site_data (dict): A dictionary containing "cookies" and "local_storage" keys with corresponding data.
        Returns:
            None
        """
        cookies = site_data["cookies"]
        local_storage = site_data["local_storage"]
        self.add_cookies_dict(cookies)
        self.add_local_storage_dict(local_storage)

    def delete_cookies_dict(self):
        """
        Deletes all cookies from the current browser session.
        Returns:
            None
        """
        self.delete_all_cookies()

    def delete_cookies_and_local_storage_dict(self):
        """
        Deletes both cookies and clears LocalStorage from the current browser session.
        Returns:
            None
        """
        self.delete_cookies_dict()
        self.delete_local_storage_dict()

    def execute_file(self, filename, *args):
        """
        Executes a JavaScript file content within the browser.
        Args:
            filename (str): The name of the JavaScript file to be executed.
            *args: Additional arguments to be passed to the JavaScript file.
        Returns:
            Any: The result of the JavaScript file execution.
        """
        if not filename.endswith(".js"):
            filename = filename + ".js"
        content = read_file(filename)
        return self.execute_script(content, *args)

    def is_in_page(self, target, wait=None, raise_exception=False):
        """
        Checks if the browser is on a page matching the specified target.
        Args:
            target (str or list): The target string or list of strings to match in the current URL.
            wait (float): Optional wait time for the check to be successful.
            raise_exception (bool): If True, raises an exception if the page is not found within the specified time.
        Returns:
            bool: True if the target is found, False otherwise.
        Raises:
            Exception: If the page is not found and raise_exception is True.
        """
        def check_page(driver, target):
            if isinstance(target, str):
                return target in driver.current_url
            else:
                for x in target:
                    if x in driver.current_url:
                        return True
                return False

        if wait is None:
            return check_page(self, target)
        else:
            time = 0
            while time < wait:
                if check_page(self, target):
                    return True

                sleep_time = 0.2
                time += sleep_time
                sleep(sleep_time)

        if raise_exception:
            raise Exception(f"Page {target} not found")
        return False

    def quit(self) -> None:
        """
        Quits the browser and performs additional cleanup.
        Returns:
            None
        """
        if hasattr(self, 'close_proxy') and callable(self.close_proxy):
            self.close_proxy()

        return super().quit()
