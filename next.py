from selenium.webdriver.common.by import By
from driver import create_mobile_driver

import time
import typer
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
        node = driver.find_element(By.CSS_SELECTOR, '.ouxiq, .LylZZ, .CHC5F')
        url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
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


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place


def replaceTransUrl(url: str):
    r = replaceMapUrl(url, "transportation")
    return r


def replaceParkingUrl(url: str):
    r = replaceMapUrl(url, "parking")
    return r


def replaceMapUrl(url: str, filter: str):
    taillUrl = f'/location?from=search&filter={filter}'
    r = None
    if r'?' in url:
        r = re.sub(r'(\/home\?|\?).*$', taillUrl, url)
    else:
        r = f'{url}{taillUrl}'
    return r


if __name__ == "__main__":
    app()
