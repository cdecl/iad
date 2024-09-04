from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from driver import create_mobile_driver

import time
import typer
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2

@app.command(name="tran")
def transport(q: str = typer.Argument("")):
    clipboard_use = False

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    try:
        node = driver.find_element(By.CSS_SELECTOR, '.ouxiq, .LylZZ, .CHC5F') # , OR conditoin
        url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    except:
        url = "Node with class 'ouxiq' and 'LylZZ' not found."

    print(f'place url 1: {url}')
    tranUrl = None

    driver.get(url)
    time.sleep(PAGE_SLEEP) 
    url = driver.current_url
    print(f'place url 2: {url}')

    if 'http' in url:
        # place = getPlaceCode(url)
        # print(f'place: {place}')
        tranUrl = replaceTransUrl(url)

        if clipboard_use:
            print(f'TRANSPORT: {tranUrl} → clipboard.copy')
            clipboard.copy(tranUrl)   
        # print(f'TRANS: {tranUrl}')

    driver.quit()
    return tranUrl


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place

def replaceTransUrl(url: str):
    tailUrl = '/location?from=search&filter=transportation'
    r = None
    if r'?' in url:
        r = re.sub(r'(\/home\?|\?).*$', tailUrl, url)
    else:
        r = f'{url}{tailUrl}'
    return r


if __name__ == "__main__":
    app()