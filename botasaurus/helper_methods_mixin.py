from datetime import datetime
from random import uniform
from time import sleep
from traceback import print_exc

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from botasaurus.output import is_slash_not_in_filename


from .decorators_utils import  create_directory_if_not_exists
from .beep_utils import beep_input
from .local_storage_driver import LocalStorage
from .opponent import Opponent
from .utils import read_file, relative_path, sleep_for_n_seconds, sleep_forever
from .wait import Wait
from .driver_about import AboutBrowser
from .accept_google_cookies import accept_google_cookies

class HelperMethodMixin():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.about: AboutBrowser = None

    def get_by_current_page_referrer(self, link, wait=None):

        # selenium.common.exceptions.WebDriverException
        
        currenturl = self.current_url
        self.execute_script(f"""
                window.location.href = "{link}";
            """)
        
        # cleaned = link.replace("https://", "").replace("http://", "")
        changed = False
        while not changed:
            if currenturl != self.current_url:
                changed = True
            sleep(0.1)

        if wait is not None and wait != 0:
            sleep(wait)

    def js_click(self, element):
        self.execute_script("arguments[0].click();",  element)
    def get_elements_or_none_by_xpath(self: WebDriver, xpath,wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_elements(By.XPATH, xpath)
            else:
                WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, xpath)))

                return self.find_elements(By.XPATH, xpath)
        except:
            return None



    def sleep(self, n):
        sleep_for_n_seconds(n)

    def prompt(self, text="Press Enter To Continue..."):
        return beep_input(text, self.about.beep)

    def short_random_sleep(self):
        sleep_for_n_seconds(uniform(2, 4))

    def long_random_sleep(self):
        sleep_for_n_seconds(uniform(6, 9))

    def sleep_forever(self):
        sleep_forever()

    def get_bot_detected_by(self):

        pmx = self.get_element_or_none(
            "//*[text()='Please verify you are a human']")
        if pmx is not None:
            return Opponent.PERIMETER_X

        clf = self.get_element_or_none_by_selector("#challenge-running")
        if clf is not None:
            return Opponent.CLOUDFLARE

        return None

    def is_bot_detected(self):
        return self.get_bot_detected_by() is not None

    def get_element_or_none(self, xpath, wait=Wait.SHORT) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.XPATH, xpath)
            else:
                return WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return None

    def get_element_or_none_by_selector(self: WebDriver, selector, wait=Wait.SHORT) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.CSS_SELECTOR, selector)
            else:
                return WebDriverWait(self, wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except:
            return None

    def get_element_by_id(self, id: str, wait=Wait.SHORT):
        cleaned = id.lstrip('#')
        return self.get_element_or_none_by_selector(f'[id="{cleaned}"]', wait)

    def get_element_or_none_by_text_contains(self, text, wait=Wait.SHORT):
        text = f'//*[contains(text(), "{text}")]'
        return self.get_element_or_none(text, wait)

    def get_element_or_none_by_text(self, text,wait=Wait.SHORT):
        text = f'//*[text()="{text}"]'

        return self.get_element_or_none(text, wait)

    def get_element_parent(element):
        return element.find_element(By.XPATH, "./..")

    def get_elements_or_none_by_selector(self: WebDriver, selector,wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_elements(By.CSS_SELECTOR, selector)
            else:
                WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                return self.find_elements(By.CSS_SELECTOR, selector)
        except:
            return None


    def text(self: WebDriver, selector: str,   wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)
        if el is None:
            # print(f'Element with selector: "{selector}" not found')
            return None

        return el.text

    def text_xpath(self: WebDriver, xpath: str,   wait=Wait.SHORT):
        el = self.get_element_or_none(
                xpath, wait)
        if el is None:
            # print(f'Element with selector: "{selector}" not found')
            return None

        return el.text

    def link(self: WebDriver, selector: str,   wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)

        if el is None:
            # print(f'Element with selector: "{selector}" not found')

            return None

        return el.get_attribute("href")


    def exists(self: WebDriver, selector: str,   wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)

        if el is None:
            # print(f'Element with selector: "{selector}" not found')

            return False

        return True

    def scroll(self, selector: str,   wait=Wait.SHORT):
        element = self.get_element_or_none_by_selector(
                selector, wait)

        if (element) is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False

    def links(self: WebDriver, selector: str,   wait=Wait.SHORT):
        els = self.get_elements_or_none_by_selector(
                selector, wait)

        if els is None:
            # print(f'Element with selector: "{selector}" not found')
            return []
        
        def extract_links(elements):
                    def extract_link(el):
                            return el.get_attribute("href")

                    return list(map(extract_link, elements))

        links = extract_links(els)

        return links

    def type(self: WebDriver, selector: str, text: str,  wait=Wait.SHORT):
        input_el = self.get_element_or_none_by_selector(
                selector, wait)
        
        if input_el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")
        
        input_el.send_keys(text)

    def click(self: WebDriver, selector, wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)
        
        if el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")
        
        self.js_click(el)

    
    def get_element_text(self, element):
        return element.get_attribute('innerText')

    def get_innerhtml(self, element):
        return element.get_attribute("innerHTML")

    def get_element_or_none_by_name(self, selector, wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_element(By.NAME, selector)
            else:
                return WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.NAME, selector)))
        except:
            return None

    def scroll_site(self):
        self.execute_script(""" 
window.scrollBy(0, 10000);
""")

    def can_element_be_scrolled(self, element):
        # <=3 is a fix to handle floating point numbers
        result = not (self.execute_script(
            "return Math.abs(arguments[0].scrollTop - (arguments[0].scrollHeight - arguments[0].offsetHeight)) <= 3", element))
        return result

    def scroll_into_view(self, element):
        return self.execute_script("arguments[0].scrollIntoView()", element)

    def scroll_element(self, element):
        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False


    def get_cookies_dict(self):
        all_cookies = self.get_cookies()
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict

    def get_local_storage_dict(self):
        storage = LocalStorage(self)
        return storage.items()

    def get_cookies_and_local_storage_dict(self):
        cookies = self.get_cookies_dict()
        local_storage = self.get_local_storage_dict()

        return {"cookies": cookies, "local_storage": local_storage}

    def add_cookies_dict(self, cookies):
        for key in cookies:
            self.add_cookie({"name": key, "value": cookies[key]})

    def add_local_storage_dict(self, local_storage):
        storage = LocalStorage(self)
        for key in local_storage:
            storage.set_item(key, local_storage[key])

    def add_cookies_and_local_storage_dict(self, site_data):
        cookies = site_data["cookies"]
        local_storage = site_data["local_storage"]
        self.add_cookies_dict(cookies)
        self.add_local_storage_dict(local_storage)

    def delete_cookies_dict(self):
        self.delete_all_cookies()

    def delete_local_storage_dict(self):
        self.execute_script("window.localStorage.clear();")
        self.execute_script("window.sessionStorage.clear();")

    def delete_cookies_and_local_storage_dict(self):
        self.delete_cookies_dict()
        self.delete_local_storage_dict()

    def organic_get(self, link,  wait=None, accept_cookies=False):
        self.get("https://www.google.com/")
        if accept_cookies:
            accept_google_cookies(self)
        self.get_by_current_page_referrer(link, wait)

    def get_google(self, accept_cookies=False):
        self.get("https://www.google.com/")
        if accept_cookies:
            accept_google_cookies(self)
        # self.get_element_or_none_by_selector('input[role="combobox"]', Wait.VERY_LONG)

    @property
    def local_storage(self):
        return LocalStorage(self)

    def get_links(self, search=None, wait=Wait.SHORT):

        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("href")

            return list(map(extract_link, elements))

        els = self.get_elements_or_none_by_selector("a", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search == None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))


    def execute_file(self, filename, *args):
        if not filename.endswith(".js"):
            filename = filename + ".js"
        content = read_file(filename)
        return self.execute_script(content, *args)
    def get_images(self, search=None, wait=Wait.SHORT):

        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("src")

            return list(map(extract_link, elements))

        els = self.get_elements_or_none_by_selector("img", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search == None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))

    def is_in_page(self, target, wait=None, raise_exception=False):

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

    def save_screenshot(self, filename=datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".png"):
        try:

            if not filename.endswith(".png"):
                filename = filename + ".png"

            if is_slash_not_in_filename(filename):
                create_directory_if_not_exists("output/screenshots/")
                filename = f'output/screenshots/{filename}'
            filename = relative_path(
                    filename, 0)
            self.get_screenshot_as_file(
                filename)
            # print('Saved screenshot at {0}'.format(final_path))
        except:
            print_exc()
            print('Failed to save screenshot')
    
    def prompt_to_solve_captcha(self, more_rules=[]):
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

        # print('General Rules of Captcha Solving')
        # print(' - Solve it Fast')

        # for t in more_rules:
        #     print(t)
        # print('- Solve it Fast')
        # print('1. If')

        return beep_input('Press fill in the captcha, the faster the less detectable, then press enter to continue ...', self.about.beep)

        # return beep_input('Press fill in the captcha and press enter to continue ...', self.about.beep)
    def quit(self) -> None:
        return super().quit()
