from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import time
import typer
import clipboard
import re
import json

app = typer.Typer()

PAGE_SLEEP = 0.2

def create_driver():
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    
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


def create_mobile_driver():
    USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/79.0.3945.88 Mobile/15E148 Safari/604.1"
    
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


@app.command()
def list(url: str = typer.Argument("")):
    if not url:
        url = clipboard.paste()
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    time.sleep(PAGE_SLEEP) 
    list_items = driver.find_elements(By.CLASS_NAME, 'list-item')

    for item in list_items:
        badge = item.find_element(By.CSS_SELECTOR, 'div.list-item__right > span')
        if '진행중' == badge.text.strip():
            href = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f'{badge.text} : {href}')

            try:
                page(href)
            except: 
                pass
            
            time.sleep(2) 


def parseGoods(s: str):
    nm = store = price = name = None 

    match = re.search(r'2.*\r?\n\r?\n(.*)', s, re.M)
    if match: nm = match.group(1).strip()

    match = re.search(r'스토어명 : (.*)', s)
    if match: store = match.group(1).strip()

    match = re.search(r'가격 : (.*)', s)
    if match: price = match.group(1).strip()

    match = re.search(r'상품명 : (.*)', s)
    if match: name = match.group(1).strip()

    return (nm, store, price, name)


@app.command()
def page(url: str = typer.Argument("")):
    if not url:
        url = clipboard.paste()
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    qinfo = driver.find_element(By.CLASS_NAME, 'quiz-info')
    q_txt = qinfo.text

    print(q_txt)
    print('-' * 20)

    ## RUN 
    pdcode = run(q_txt)

    quizAnswer = driver.find_element(By.ID, 'quizAnswer')
    quizAnswer.send_keys(pdcode)

    save_button = driver.find_element(By.ID, 'saveBtn')
    save_button.click()

    print(f'{pdcode} → save_button.click()')
    driver.quit()


@app.command()
def run(q: str = typer.Argument("")):
    if not q:
        q = clipboard.paste()
    
    gd = parseGoods(q)
    print(gd)
    
    q = gd[0]
    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)
    
    driver = create_driver()
    driver.get(url)
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    # JavaScript 코드
    script = """
    var elements = document.querySelectorAll('._product');
    var elementArray = [...elements];
    var results = [];
    var i = 1
    elementArray.forEach(function(node) {
        url = node.querySelector("a").getAttribute("href");
        name = node.querySelector("strong.name").textContent;
        price = node.querySelector("div.price span.txt strong").textContent;
        store = node.querySelector("div.store span.txt").textContent;

        const r = {
            "name": name,
            "price": price,
            "store": store,
            "url": url
        };

        results.push(r);
        i++;
    });
    return JSON.stringify(results);
    """

    # JavaScript 코드 실행 및 결과 가져오기
    results = driver.execute_script(script)
    # print(results)

    items = json.loads(results)
    price_match = False
    pdcode = None

    for item in items:
        if (item["store"] == gd[1] and 
            item["price"].replace(',', '') == gd[2].replace(',', '') and 
            item["name"].strip() == gd[3].strip()):
            print(item)
            pdcode = getUrlCode(item["url"], driver)
            price_match = True
            exit
 
    if not price_match:
        for item in items:
            if (item["store"] == gd[1] and 
                item["name"].strip() == gd[3].strip()):
                print(item)
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
    print(pdcode)
    clipboard.copy(pdcode)

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