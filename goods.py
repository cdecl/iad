from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from driver import create_driver, create_mobile_driver

import time
import typer
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2


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
                except Exception:
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

    qinfo = driver.find_element(By.CLASS_NAME, 'mission__guide')
    q_txt = qinfo.text
    print(q_txt)

    # RUN
    pdcode = run(q_txt)

    if pdcode:
        save_action(driver, pdcode)
        success = True
        print(f'{pdcode} → save_button.click(success)')
    else:
        print(f'{pdcode} → save_button.click(failed)')

    driver.quit()
    return success


def save_action(driver, pdcode):
    quizAnswer = driver.find_element(By.NAME, 'quizAnswer')
    quizAnswer.send_keys(pdcode)
    # save_button = driver.find_element(By.ID, 'saveBtn')
    # save_button.click()
    result = driver.execute_script("return document.querySelector('#saveBtn').click();")
    print(f'> SAVE_ACTION : {result}')

    alert = Alert(driver)
    print(f'> SAVE_ALERT : {alert.text}')
    alert.accept()


def parseGoods(s: str):
    keyword = store = price = name = None

    # match = re.search(r'2.*\r?\n\r?\n(.*)', s, re.M)
    # if match: nm = match.group(1).strip()

    match = re.search(r'스토어명 : (.*)', s)
    if match:
        store = match.group(1).strip()

    match = re.search(r'가격 : (.*)', s)
    if match:
        price = match.group(1).strip()
        if not price:
            price = 0

    match = re.search(r'상품명 : (.*)', s)
    if match:
        name = match.group(1).strip()

    if not keyword:
        keyword = name

    return [keyword, store, price, name]


@app.command()
def run(q: str = typer.Argument("")):
    clipboard_use = False
    pdcode = None

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    goodsinfo = parseGoods(q)
    print(f'parseGoods: {goodsinfo}')

    if not goodsinfo[1]:
        print("QUIZ 형식이 맞지 않습니다.")
        return None

    pdcode = search_naver(goodsinfo[0], goodsinfo[1], goodsinfo[2], goodsinfo[3])

    if clipboard_use:
        clipboard.copy(pdcode)

    return pdcode


def search_naver(keyword: str, store_in: str, price_in: str, name_in: str):
    q = keyword
    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)

    driver = create_driver()
    driver.get(url)
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    products = driver.find_elements(By.CSS_SELECTOR, '._product')
    results = []

    for product in products:
        try:
            url = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            name = product.find_element(By.CSS_SELECTOR, 'strong.name').text
            price = product.find_element(By.CSS_SELECTOR, 'div.price span.txt strong').text
            store = product.find_element(By.CSS_SELECTOR, 'div.store span.txt').text

            result = {
                "name": name,
                "price": price,
                "store": store,
                "url": url
            }
            results.append(result)
        except Exception:
            continue

    price_match = False
    pdcode = None

    for item in results:
        if (item["store"] == store_in and item["price"].replace(',', '') == price_in.replace(',', '') and item["name"].strip() == name_in.strip()):
            print(f'for item in results: {item}')
            pdcode = getUrlCode(item["url"], driver)
            price_match = True
            exit

    if not price_match:
        for item in results:
            if (item["store"] == store_in and item["name"].strip() == name_in.strip()):
                print(f'if not price_match: {item}')
                pdcode = getUrlCode(item["url"], driver)
                exit

    driver.quit()
    return pdcode


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
