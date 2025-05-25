from selenium import webdriver 
from selenium.webdriver import FirefoxOptions

def get_driver():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    return webdriver.Firefox(options = opts) 
