from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

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


def extract_consonants(hangul_text: str) -> str:
    if hangul_text is None:
        hangul_text = ""

    CHOSUNG_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]

    result = []
    for char in hangul_text:
        # 한글 유니코드 범위 안에 있는지 확인
        if '가' <= char <= '힣':
            code = ord(char) - ord('가')
            chosung_index = code // 588
            result.append(CHOSUNG_LIST[chosung_index])
        else:
            result.append(char)  # 한글이 아닌 경우 그대로 추가

    return ''.join(result)


def getFilter(s: str):
    match = re.search(r'3. \[([^]]+)\].*\[([^]]+)번째\]', s)
    info = None
    if match:
        info = match.groups()
        print(info)
    return info


def getFilterConsonants(s: str):
    match = re.search(r'초성은 (.*) 입니다.', s)
    info = None
    if match:
        info = match.group(1)
    return info

def getFilterCode(s: str):
    ret = None
    code = {
        "명소": "100",
        "놀거리": "30",
        "취미생활": "50"
    }
    if s in code:
        ret = code[s]
    return ret

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

    for item in list_items:
        badge = item.find_element(By.CSS_SELECTOR, 'div.list-item__right > span')
        if '진행중' == badge.text.strip():
            href = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f'{badge.text} : {href}')

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
    order = int(info[1])
    filterCode = getFilterCode(info[0])
    quisConsonants = getFilterConsonants(info_txt)

    print(f'copyTxt: {txt}')
    print(f'filterCode: {filterCode}, order: {order}')

    placeName = None
    if filterCode:
        placeName = place(order, filterCode, txt, quisConsonants)
        placeNameConsonants = extract_consonants(placeName)
        print(f'추출자음: {placeNameConsonants} / 예시자음: {quisConsonants}')

        if placeName and placeNameConsonants == quisConsonants:
            searchAnswer = driver.find_element(By.ID, 'searchAnswer')
            searchAnswer.send_keys(placeName)
            saveBtn = driver.find_element(By.ID, 'saveBtn')
            saveBtn.click()
            success = True
            print(f'{placeName} → save_button.click(success)')
        else:
            print(f'{placeName} → save_button.click(failed)')

    driver.quit()
    return success

@app.command()
def code(idx: int, id: str, filter = typer.Argument("100")):
    driver = create_driver()
    retCode = code_internal(driver, idx, id, filter)
    driver.quit()
    return retCode

def code_internal(driver, idx: int, id: str, filter: str, quisConsonants = typer.Argument("")):
    retCode = None
    url = f'https://m.place.naver.com/restaurant/{id}/around?entry=pll&filter={filter}'
    print(url)

    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    # '.xBZDS' 클래스를 가진 모든 요소 찾기
    elements = driver.find_elements(By.CSS_SELECTOR, '.xBZDS')
    results = []
    for el in elements:
        results.append(f"{el.text}")

    print(f'quisConsonants : {quisConsonants}')
    if quisConsonants:
        for r in results:
            extract = extract_consonants(r)
            if quisConsonants == extract:
                print(f'자음매치: {r}')
                retCode = r
        
    if not retCode:
        for i, r in enumerate(results, start=1):
            if i == (idx - 1):
                print(f'{i}: {r}')
            if i == idx:
                print(f'→ {i}: {r}')
                retCode = r

    return retCode

# 놀거리 
@app.command()
def play(idx: int, filter: str = typer.Argument("30"), q: str = typer.Argument("")):
    return place(idx, filter, q)

#명소 
@app.command()
def place(idx: int, filter: str = typer.Argument("100"), q: str = typer.Argument(""), quistext: str = typer.Argument("")):
    clipboard_use = False
    placeName = None

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    url = f'https://m.search.naver.com/search.naver?query={q}'
    print(url)

    driver = create_driver()
    driver.get(url)

    # 페이지 로딩을 기다림
    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    try:
        # 'ouxiq' 클래스를 가진 노드 찾기
        node = driver.find_element(By.CSS_SELECTOR, '.ouxiq')
        url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    except:
        try:
            # 'LylZZ' 클래스를 가진 노드 찾기
            node = driver.find_element(By.CSS_SELECTOR, '.LylZZ')
            url = node.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        except:
            url = "Node with class 'ouxiq' and 'LylZZ' not found."

    print(f'url: {url}')
    place = getPlaceCode(url)
    print(f'place: {place}')
    
    if place:
        placeName = code_internal(driver, idx, place, filter, quistext)
        if clipboard_use: clipboard.copy(placeName)

    driver.quit()
    return placeName


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place



if __name__ == "__main__":
    app()