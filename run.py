from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import typer
import clipboard

app = typer.Typer()

# Chrome 웹드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

@app.command()
def code(id: str, idx: int):
    # 페이지 호출
    url = f'https://m.place.naver.com/restaurant/{id}/around?entry=pll&filter=100'
    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(1)  # 필요에 따라 조정

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

if __name__ == "__main__":
    app()