from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import unittest
import json


def create_common_driver(user_agent: str):
    USER_AGENT = user_agent
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 헤드리스 모드
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
    chrome_options.add_argument("--no-sandbox")  # 샌드박스 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화
    chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화‘
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f"user-agent={USER_AGENT}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver   

def create_driver():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    return create_common_driver(user_agent)

def create_mobile_driver():
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.88 Mobile/15E148 Safari/604.1"
    return create_common_driver(user_agent)


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