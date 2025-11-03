from selenium import webdriver 
from selenium.webdriver import FirefoxOptions

def get_driver(proxy=None):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    if proxy is not None:
        opts.add_argument('--proxy-server=%s' % proxy)
    return webdriver.Firefox(options = opts) 
