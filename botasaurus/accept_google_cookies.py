from time import sleep

def verify_cookies(driver):

        def check_page():
            # can be socks too..
            return  "NID" in driver.get_cookies_dict()

        time = 0
        WAIT = 8
        
        while time < WAIT:
                if check_page():
                    return True

                sleep_time = 0.1
                time += sleep_time
                sleep(sleep_time)

        raise Exception(f"Unable to consent Cookies")

def accept_google_cookies(driver):
                input_el = driver.get_element_or_none_by_selector('[role="combobox"]', 16)
                if input_el is None:
                    raise Exception("Unabe to load Google")
                else:
                    accept_cookies_btn = driver.get_element_or_none_by_selector("button#L2AGLb", None)
                    if accept_cookies_btn is None:
                        pass
                    else:
                        accept_cookies_btn.click()
                        verify_cookies(driver)    