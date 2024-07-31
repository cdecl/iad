from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import typer
import clipboard
import re
import json

app = typer.Typer()

PAGE_SLEEP = 0.2

def parseGoods(s: str):
    nm = store = price = name = None 

    match = re.search(r'2.*\r?\n\r?\n(.*)', s)
    if match: nm = match.group(1).strip()

    match = re.search(r'스토어명 : (.*)', s)
    if match: store = match.group(1).strip()

    match = re.search(r'가격 : (.*)', s)
    if match: price = match.group(1).strip()

    match = re.search(r'상품명 : (.*)', s)
    if match: name = match.group(1).strip()

    return (nm, store, price, name)

@app.command()
def run(q: str = typer.Argument("")):
    if not q:
        q = clipboard.paste()
    
    gd = parseGoods(q)
    print(gd)
    
    q = gd[0]
    url = f'https://m.search.naver.com/search.naver?query={q}'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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

    for item in items:
        if (item["store"] == gd[1] and 
            item["price"].replace(',', '') == gd[2].replace(',', '') and 
            item["name"].strip() == gd[3].strip()):
            print(item)
            page(item["url"])
            exit
 
    driver.quit()

def page(url: str):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    current_url = driver.current_url
    print(current_url)

    pdcode = getProductCode(current_url)
    print(pdcode)
    clipboard.copy(pdcode)

    driver.quit()


def getProductCode(url: str):
    match = re.search(r'/(?:products)/(\d+)', url)
    extracted_value = "값을 추출할 수 없습니다."
    if match:
        extracted_value = match.group(1)
    return extracted_value



if __name__ == "__main__":
    app()