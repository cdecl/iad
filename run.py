from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import typer
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2

@app.command()
def code(idx: int, id: str, filter = typer.Argument("100")):
    url = f'https://m.place.naver.com/restaurant/{id}/around?entry=pll&filter={filter}'
    print(url)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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

    i = 1
    # 결과 출력
    for result in results:
        if i == idx:
            print(result)
            clipboard.copy(result.split(' ')[1])
        i += 1
    driver.quit()

# 놀거리 
@app.command()
def play(idx: int, filter: str = typer.Argument("30")):
    place(idx, filter)

#명소 
@app.command()
def place(idx: int, filter: str = typer.Argument("100")):
    q = clipboard.paste()

    url = f'https://m.search.naver.com/search.naver?query={q}'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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
    driver.quit()
    
    code(idx, place, filter)


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    extracted_value = "값을 추출할 수 없습니다."
    if match:
        extracted_value = match.group(1)
    return extracted_value



if __name__ == "__main__":
    app()