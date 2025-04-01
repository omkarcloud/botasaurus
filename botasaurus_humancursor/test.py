from botasaurus.browser import browser, Driver
from src.botasaurus_humancursor import WebCursor

@browser()
def test(driver: Driver, data):
    driver.get("https://nopecha.com/demo/cloudflare")
    driver.short_random_sleep()  # Wait for page to fully load

    # Initialize HumanCursor
    cursor = WebCursor(driver)

    cursor.click([158,286])

    driver.prompt()


test()
