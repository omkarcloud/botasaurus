import traceback
from datetime import datetime
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random
from time import sleep
from .beep_utils import beep_input
from .local_storage_driver import LocalStorage
from .opponent import Opponent
from .utils import relative_path, sleep_for_n_seconds, sleep_forever


class BoseDriver(webdriver.Chrome):

    def get_by_current_page_referrer(self, link, wait=None):

        # selenium.common.exceptions.WebDriverException
        self.execute_script(f"""
                window.location.href = "{link}";
            """)
        if wait is not None and wait != 0:
            sleep(wait)

    def js_click(self, element):
        self.execute_script("arguments[0].click();",  element)

    def sleep(self, n):
        sleep_for_n_seconds(n)

    def prompt(self, text="Press Enter To Continue..."):
        return beep_input(text, self.beep)

    def short_random_sleep(self):
        sleep_for_n_seconds(random.uniform(2, 4))

    def long_random_sleep(self):
        sleep_for_n_seconds(random.uniform(6, 9))

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

    def get_element_or_none(self, xpath, wait=None) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.XPATH, xpath)
            else:
                return WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return None

    def get_element_or_none_by_selector(self: WebDriver, selector, wait=None) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.CSS_SELECTOR, selector)
            else:
                return WebDriverWait(self, wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except:
            return None

    def get_element_by_id(self, id: str, wait=None):
        cleaned = id.lstrip('#')
        return self.get_element_or_none_by_selector(f'[id="{cleaned}"]', wait)

    def get_element_or_none_by_text_contains(self, text, wait=None):
        text = f'//*[contains(text(), "{text}")]'
        return self.get_element_or_none(text, wait)

    def get_element_or_none_by_text(self, text, wait=None):
        text = f'//*[text()="{text}"]'

        return self.get_element_or_none(text, wait)

    def get_element_parent(element):
        return element.find_element(By.XPATH, "./..")

    def get_elements_or_none_by_selector(self: WebDriver, selector, wait=None):
        try:
            if wait is None:
                return self.find_elements(By.CSS_SELECTOR, selector)
            else:
                WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                return self.find_elements(By.CSS_SELECTOR, selector)
        except:
            return None

    def get_element_text(self, element):
        return element.get_attribute('innerText')

    def get_innerhtml(self, element):
        return element.get_attribute("innerHTML")

    def get_element_or_none_by_name(self, selector, wait=None):
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

    def scroll_element(self, element):

        did_element_scroll = self.execute_script(
            "return Math.round(arguments[0].scrollTop) === Math.round(Math.round(arguments[0].scrollHeight) - Math.round(arguments[0].offsetHeight))", element)

        if did_element_scroll:
            return False
        else:
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True

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

    def organic_get(self, link, wait=None):
        self.get("https://www.google.com/")
        self.get_by_current_page_referrer(link, wait)

    def get_google(self):
        self.get("https://www.google.com/")
        # self.get_element_or_none_by_selector('input[role="combobox"]', Wait.VERY_LONG)

    @property
    def local_storage(self):
        return LocalStorage(self)

    def get_links(self, search=None, wait=None):

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

    def get_images(self, search=None, wait=None):

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
            saving_screenshot_at = relative_path(
                f'{self.task_path}/{filename}', 0)
            self.get_screenshot_as_file(
                saving_screenshot_at)
        except:
            traceback.print_exc()
            print('Failed to save screenshot')

    def prompt_to_solve_captcha(self):
        print('')
        print('   __ _ _ _    _                          _       _           ')
        print('  / _(_) | |  (_)                        | |     | |          ')
        print(' | |_ _| | |   _ _ __      ___ __ _ _ __ | |_ ___| |__   __ _ ')
        print(' |  _| | | |  | | `_ \    / __/ _` | `_ \| __/ __| `_ \ / _` |') 
        print(' | | | | | |  | | | | |  | (_| (_| | |_) | || (__| | | | (_| |')   # Tells user to solve captcha
        print(' |_| |_|_|_|  |_|_| |_|   \___\__,_| .__/ \__\___|_| |_|\__,_|')
        print('                                   | |                        ')
        print('                                   |_|                        ')
        print('')

        return beep_input('Press fill in the captcha and press enter to continue ...', self.beep)
