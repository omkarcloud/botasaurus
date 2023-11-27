from seleniumwire import webdriver
from botasaurus.helper_methods_mixin import HelperMethodMixin
from selenium import webdriver as normaldriver


                  

class AntiDetectDriverSeleniumWire(webdriver.Chrome, HelperMethodMixin):
    pass


class AntiDetectFirefoxDriverSeleniumWire(webdriver.Firefox, HelperMethodMixin):
    pass


class AntiDetectFirefoxDriver(normaldriver.Firefox, HelperMethodMixin):
    pass

