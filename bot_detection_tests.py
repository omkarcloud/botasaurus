from botasaurus.browser import browser, Driver

def test_browserscan_bot_detection(driver: Driver):
    """
    Tests against BrowserScan's bot detection system.
    Visits BrowserScan's bot detection demo page.
    """
    print("Running BrowserScan Bot Detection test...")
    driver.get("https://www.browserscan.net/bot-detection")
    driver.sleep(3)
    print("✅ BrowserScan Bot Detection test completed")


def test_fingerprint_bot_detection(driver: Driver):
    """
    Tests against Fingerprint's bot detection system.
    Visits Fingerprint's bot detection product page.
    """
    print("Running Fingerprint Bot Detection test...")
    driver.get("https://fingerprint.com/products/bot-detection/")
    driver.sleep(4)
    print("✅ Fingerprint Bot Detection test completed")


def test_datadome_bot_detection(driver: Driver):
    """
    Tests against Datadome's bot detection system.
    Visits a demo page protected by Datadome.
    """
    print("Running Datadome Bot Detection test...")
    driver.get("https://fingerprint-scan.com/")
    driver.sleep(3)
    print("✅ Datadome Bot Detection test completed")


def test_cloudflare_turnstile(driver: Driver):
    """
    Tests bypassing Cloudflare Turnstile CAPTCHA.
    Visits a demo page with Cloudflare Turnstile implementation.
    """
    print("Running Cloudflare Turnstile test...")
    driver.get("https://turnstile.zeroclover.io/", bypass_cloudflare=True)
    driver.sleep(3)
    print("✅ Cloudflare Turnstile test completed")


def test_cloudflare_waf(driver: Driver):
    """
    Tests bypassing Cloudflare Web Application Firewall (WAF).
    Visits a demo page protected by Cloudflare WAF.
    """
    print("Running Cloudflare WAF test...")

    driver.get("https://nopecha.com/demo/cloudflare", bypass_cloudflare=True)
    driver.sleep(3)
    print("✅ Cloudflare WAF test completed")


@browser()
def run_bot_tests(driver: Driver, _):
    """
    Main function to run all bot detection tests.
    Executes various tests to check bypass capabilities against different security systems.
    """
    test_cloudflare_waf(driver)
    test_browserscan_bot_detection(driver)
    test_fingerprint_bot_detection(driver)
    test_datadome_bot_detection(driver)
    test_cloudflare_turnstile(driver)
    
    


if __name__ == "__main__":
    run_bot_tests()