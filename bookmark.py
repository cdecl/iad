from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from driver import create_driver, create_mobile_driver
from run import getPlaceCode

import time
import typer
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2

@app.command()
def home(q: str = typer.Argument("")):
    clipboard_use = False
    placeName = None

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)

    driver = create_mobile_driver(True)
    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    try:
        node = driver.find_element(By.CSS_SELECTOR, '.ouxiq, .LylZZ, .CHC5F') # , OR conditoin
        url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    except:
        url = "Node with class 'ouxiq' and 'LylZZ' not found."

    print(f'place url: {url}')

    if 'http' in url:
        place = getPlaceCode(url)
        print(f'place: {place}')

        bookmarkUrl = f'https://m.place.naver.com/restaurant/{place}/home?entry=pll#bookmark'
        driver.get(bookmarkUrl)
        time.sleep(PAGE_SLEEP) 

        try:
            savelist = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".swt-save-group-info"))
            )
            time.sleep(PAGE_SLEEP)
            savelist = driver.find_elements(By.CSS_SELECTOR, '.swt-save-group-info')
            cnt = len(savelist)
            print(f'savelist: {cnt}')
            savelist[1].click()
            print('onclick')

            savebtn = driver.find_element(By.CSS_SELECTOR, '.swt-save-btn')
            savebtn.click()

            _ = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".O0gMc"))
            )
            
            bookmarkLink = driver.find_element(By.CSS_SELECTOR, '.O0gMc > a')
            savesUrl = bookmarkLink.get_attribute('href')

            print(savesUrl)
            driver.get(savesUrl)
            
            pubBtn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.A776rV"))
            )
            pubBtn.click()

            myBtn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a._spi_input_copyurl"))
            )
            myUrl = myBtn.get_attribute('href')
            print(f'MYURL: {myUrl}')
            
        except Exception as e:
            print(f'Exception: {e}')

    driver.quit()


if __name__ == "__main__":
    app()