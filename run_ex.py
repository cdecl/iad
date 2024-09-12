from selenium.webdriver.common.by import By
from driver import create_mobile_driver, create_driver

import time
import typer
from typing import List
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2


def search_naver(driver, q):
    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)

    driver.get(url)
    time.sleep(PAGE_SLEEP)

    try:
        nodes = driver.find_elements(By.CSS_SELECTOR, '.ouxiq, .LylZZ, .CHC5F, .IPtqD')
        for node in nodes:
            url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if 'tivan.naver.com' not in url:
                break
    except Exception:
        url = "Node with class '.ouxiq, .LylZZ, .CHC5F' not found."
    return url


@app.command(name="tran")
def transport(q: str = typer.Argument("")):
    clipboard_use = False

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    driver = create_mobile_driver()
    url = search_naver(driver, q)

    print(f'place url 1: {url}')
    tranUrl = None

    driver.get(url)
    time.sleep(PAGE_SLEEP)
    url = driver.current_url
    print(f'place url 2: {url}')

    if 'http' in url:
        tranUrl = replaceTransUrl(url)

        if clipboard_use:
            print(f'TRANSPORT: {tranUrl} → clipboard.copy')
            clipboard.copy(tranUrl)

    driver.quit()
    return tranUrl


@app.command(name="parking")
def parking(q: str = typer.Argument("")):
    clipboard_use = False

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    driver = create_mobile_driver()
    url = search_naver(driver, q)

    print(f'place url 1: {url}')
    tranUrl = None

    driver.get(url)
    time.sleep(PAGE_SLEEP)
    url = driver.current_url
    print(f'place url 2: {url}')

    if 'http' in url:
        tranUrl = replaceParkingUrl(url)

        if clipboard_use:
            print(f'PARKING: {tranUrl} → clipboard.copy')
            clipboard.copy(tranUrl)

    driver.quit()
    return tranUrl


def scroll_and_load(driver, scroll_pause_time=0.5):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


@app.command()
def goods(args: List[str] = typer.Argument(...)):
    clipboard_use = True
    gdcode = None

    q = ''.join(args[:-1])
    store = args[-1]
    print(f'q={q}, store={store}')

    url = f'https://msearch.shopping.naver.com/search/all?bt=-1&query={q}'
    print(url)

    driver = create_driver()
    driver.get(url)
    scroll_and_load(driver)

    products = driver.find_elements(By.CSS_SELECTOR, '.product_info_main__piyRs')

    for product in products:
        try:
            url = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            name = product.find_element(By.CSS_SELECTOR, '.product_info_tit__c5_pb').text
            store_txt = product.find_element(By.CSS_SELECTOR, '.product_mall__v9966').text
            # print(f'name={name}, store:{store_txt}')

            if store in store_txt:
                gdcode = getUrlCode(url, driver)
                print(f'name: {name}')
                print(f'gdcode : {gdcode}')
                exit

        except Exception:
            continue

    if clipboard_use and gdcode:
        # gdcode = gdcode[:6]
        print(f'GOODSCODE: {gdcode} → clipboard.copy')
        clipboard.copy(gdcode)

    driver.quit()
    return gdcode


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place


def replaceHomeSaveUrl(url: str):
    if '?' not in url:
        url += '?'

    r = re.sub(r'\?.*$', '?from=search', url)
    return r


def replaceTransUrl(url: str):
    r = replaceMapUrl(url, "transportation")
    return r


def replaceParkingUrl(url: str):
    r = replaceMapUrl(url, "parking")
    return r


def replaceMapUrl(url: str, filter: str):
    # taillUrl = f'/location?entry=pll&filter={filter}'
    taillUrl = f'/location?from=search&filter={filter}'
    r = None
    if r'?' in url:
        r = re.sub(r'(\/home\?|\?).*$', taillUrl, url)
    else:
        r = f'{url}{taillUrl}'
    return r


def getUrlCode(url: str, driver):
    # driver = create_driver()
    driver.get(url)
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    current_url = driver.current_url
    print(current_url)

    pdcode = getProductCode(current_url)
    print(f'FOUND : {pdcode}')

    return pdcode
    # driver.quit()


def getProductCode(url: str):
    match = re.search(r'/(?:products)/(\d+)', url)
    extracted_value = f"값을 추출할 수 없습니다 : {url}"
    if match:
        extracted_value = match.group(1)
    return extracted_value


if __name__ == "__main__":
    app()
