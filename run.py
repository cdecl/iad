from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import typer
import clipboard
import re

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

@app.command()
def code(idx: int, id: str, filter = typer.Argument("100")):
    driver = create_driver()
    code_internal(idx, id, filter, driver)
    driver.quit()

def code_internal(idx: int, id: str, filter: str, driver):
    url = f'https://m.place.naver.com/restaurant/{id}/around?entry=pll&filter={filter}'
    print(url)

    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    # JavaScript 코드
    script = """
    var elements = document.querySelectorAll('.xBZDS');
    var elementArray = [...elements];
    var results = [];
    var i = 1
    elementArray.forEach(function(element) {
        results.push(i + ": " + element.textContent);
        i++;
    });
    return results;
    """

    # JavaScript 코드 실행 및 결과 가져오기
    results = driver.execute_script(script)
    # print(results)

    i = 1
    # 결과 출력
    for result in results:
        if i == (idx - 1):
            print(result)
        if i == idx:
            print("→", result)
            clipboard.copy(result.split(' ')[1])
        i += 1
    

# 놀거리 
@app.command()
def play(idx: int, filter: str = typer.Argument("30")):
    place(idx, filter)

#명소 
@app.command()
def place(idx: int, filter: str = typer.Argument("100")):
    q = clipboard.paste()

    url = f'https://m.search.naver.com/search.naver?query={q}'

    driver = create_driver()
    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    # JavaScript 코드
    script = """
    var result = "Node with class 'ouxiq' not found."
    var node = document.querySelector(".ouxiq");
    if (node) {
        url = node.querySelector("a").getAttribute("href");
        result = url
    }
    else {
        node = document.querySelector(".LylZZ");
        if (node) {
            url = node.querySelector("a").getAttribute("href");
            result = url
        }
    }

    return result
    """

    # JavaScript 코드 실행 및 결과 가져오기
    results = driver.execute_script(script)
    print(f'results: {results}')

    place = getPlaceCode(results)
    print(f'place: {place}')
    
    code_internal(idx, place, filter, driver)
    driver.quit()


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    extracted_value = "값을 추출할 수 없습니다."
    if match:
        extracted_value = match.group(1)
    return extracted_value



if __name__ == "__main__":
    app()