from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import unittest
import json


def create_common_driver(user_agent: str, debugMode: bool = False):
    USER_AGENT = user_agent
    chrome_options = Options()

    if debugMode:
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    chrome_options.add_argument("--headless=new")  # 헤드리스 모드
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
    chrome_options.add_argument("--no-sandbox")  # 샌드박스 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화
    chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화‘
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f"user-agent={USER_AGENT}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver   

def create_driver(debugMode: bool = False):
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    return create_common_driver(user_agent, debugMode)

def create_mobile_driver(debugMode: bool = False):
    user_agent = r'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
    return create_common_driver(user_agent, debugMode)


class TestCase01(unittest.TestCase):
    def test_http(self): 
        url = 'https://httpbin.org/get'
        driver = create_driver()
        driver.get(url)
        
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        dicBody= json.loads(body.text)

        rurl = dicBody['url']
        self.assertEqual(rurl, url, msg=f'rurl')

        driver.quit()