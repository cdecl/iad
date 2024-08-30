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

def getFilter(s: str):
    match = re.search(r'.*(주변정류소).*', s)
    info = None
    if match:
        info = match.groups()
        print(info)
    return info


@app.command()
def list(verbose: bool = typer.Option(False, "-v/", help="verbose mode"), interval: int = typer.Option(5, "--i/", "-i/", help="interval"), url: str = typer.Argument("")):
    if not url:
        print("url is missing !!")
        return 
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    time.sleep(PAGE_SLEEP) 
    list_items = driver.find_elements(By.CLASS_NAME, 'list-item')

    list_cnt = len(list_items)
    for idx, item in enumerate(list_items, start=1):
        badge = item.find_element(By.CSS_SELECTOR, 'div.list-item__right > span')
        if '진행중' == badge.text.strip():
            href = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f'{badge.text} ({idx}/{list_cnt}): {href}')

            if not verbose:
                try:
                    success = page(href)
                    if success:
                        time.sleep(interval) 
                        print(f'interval: {interval}sec')
                except: 
                    pass
        print("-" * 40)
        print()

@app.command()
def page(url: str):
    success = False
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    copyTxt = driver.find_element(By.CSS_SELECTOR, '#copyTxt')
    txt = copyTxt.text

    quiz_info = driver.find_element(By.CSS_SELECTOR, 'div.quiz-info')
    info_txt = quiz_info.text
    print(f'info: {info_txt}')

    info = getFilter(info_txt)

    if info:        
        print(f'copyTxt: {txt}')
        trasportUrl = transport(txt)
        print(f'TRANS: {trasportUrl}')

        if trasportUrl:
            searchAnswer = driver.find_element(By.ID, 'searchAnswer')
            searchAnswer.send_keys(trasportUrl)

            saveBtn = driver.find_element(By.ID, 'saveBtn')
            saveBtn.click()
            success = True
            print(f'{trasportUrl} → save_button.click(success)')
        else:
            print(f'{trasportUrl} → save_button.click(failed)')
    else:
        print("TELNO MODE")
        telnoText = telno(txt)
        telnoText = telnoText.replace('-', '')

        searchAnswer = driver.find_element(By.ID, 'searchAnswer')
        searchAnswer.send_keys(telnoText)
        saveBtn = driver.find_element(By.ID, 'saveBtn')
        saveBtn.click()
        success = True
        print(f'TELNO: {telnoText} → save_button.click(success)')

    driver.quit()
    return success


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

    print(f'place url: {url}')
    tranUrl = None

    if 'http' in url:
        place = getPlaceCode(url)
        print(f'place: {place}')

        tranUrl = f'https://m.place.naver.com/place/{place}/location?from=search&filter=transportation'     

        if clipboard_use:
            print(f'TRANSPORT: {tranUrl} → clipboard.copy')
            clipboard.copy(tranUrl)   
        # print(f'TRANS: {tranUrl}')

    driver.quit()
    return tranUrl


@app.command()
def telno(q: str = typer.Argument("")):
    clipboard_use = False
    placeName = None

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

    print(f'place url: {url}')
    telnoText = None

    if 'http' in url:
        driver.get(url)
        try:
            tno = driver.find_element(By.CSS_SELECTOR, '.xlx7Q')
            telnoText = tno.text
            print(f'TELNO: {telnoText}')

            if clipboard_use:
                print(f'TELNO: {telnoText} → clipboard.copy')
                clipboard.copy(telnoText)
        except:
            print('NOT FOUND')

    driver.quit()
    return telnoText


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place



if __name__ == "__main__":
    app()