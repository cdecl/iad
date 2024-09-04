from selenium.webdriver.common.by import By

from driver import create_mobile_driver
from next import transport, parking, search_naver
import time
import typer
import clipboard
import re

app = typer.Typer()

PAGE_SLEEP = 0.2

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

def getPlaceFilter(s: str):
    match = re.search(r'3. \[([^]]+)\].*\[([^]]+)번째\]', s)
    info = None
    if match:
        info = match.groups()
        print(info)
    return info

def getTransFilter(s: str):
    match = re.search(r'.*(주변정류소).*', s)
    info = None
    if match:
        info = match.groups()
        print(info)
    return info


def getParkingFilter(s: str):
    match = re.search(r'.*(주차장).*', s)
    info = None
    if match:
        info = match.groups()
        print(info)
    return info

def getTelnoFilter(s: str):
    match = re.search(r'.*(번호만 입력).*', s)
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
                    print('EXCEPT: PAGE EXCUTE') 

        print("-" * 40)
        print()

@app.command()
def page(url: str):
    success = False
    print(url)

    driver = create_mobile_driver()
    driver.get(url)

    time.sleep(PAGE_SLEEP)  # 필요에 따라 조정

    copyTxt, info_txt = getQuizInfo(driver)
    print(f'info: {info_txt}')

    info = getPlaceFilter(info_txt)
    if info:   
        print(">> PLACE_ACTION")
        success = place_action(driver, copyTxt, info_txt, info)
    else:
        info = getTransFilter(info_txt)
        if info:  
            print(">> TRANPORT_ACTION")
            success = tranport_action(driver, copyTxt)
        else:
            info = getParkingFilter(info_txt)
            if info: 
                print(">> PARKING_ACTION")
                success = parking_action(driver, copyTxt)
            else:
                info = getTelnoFilter(info_txt)
                if info: 
                    print(">> TELNO_ACTION")
                    success = telno_action(driver, copyTxt)
                else:
                    print('해당 쿼즈 필터가 없습니다.')
                    success = False

    driver.quit()
    return success

def getQuizInfo(driver):
    copyTxtNode = driver.find_element(By.CSS_SELECTOR, '#copyTxt')
    copyTxt = copyTxtNode.text

    quiz_info = driver.find_element(By.CSS_SELECTOR, 'div.quiz-info')
    info_txt = quiz_info.text
    return copyTxt, info_txt

def place_action(driver, txt, info_txt, placeInfo):
    order = int(placeInfo[1])
    filterCode = getFilterCode(placeInfo[0])
    quisConsonants = getFilterConsonants(info_txt)

    print(f'copyTxt: {txt}')
    print(f'filterCode: {filterCode}, order: {order}')

    placeName = None
    if filterCode:
        placeName = place(order, filterCode, txt, quisConsonants)
        placeNameConsonants = extract_consonants(placeName)
        print(f'추출자음: {placeNameConsonants} / 예시자음: {quisConsonants}')

        if placeName and placeNameConsonants == quisConsonants:
            save_action(driver, placeName)
            success = True
            print(f'{placeName} → save_button.click(success)')
        else:
            print(f'{placeName} → save_button.click(failed)')
    return success

def tranport_action(driver, copyTxt):
    print(f'copyTxt: {copyTxt}')
    trasportUrl = transport(copyTxt)
    print(f'trasportUrl: {trasportUrl}')    

    if trasportUrl:
        save_action(driver, trasportUrl)
        success = True
        print(f'{trasportUrl} → save_button.click(success)')
    else:
        print(f'{trasportUrl} → save_button.click(failed)')
    return success

def parking_action(driver, copyTxt):
    print(f'copyTxt: {copyTxt}')
    parkingtUrl = parking(copyTxt)
    print(f'parkingtUrl: {parkingtUrl}')

    if parkingtUrl:
        save_action(driver, parkingtUrl)
        success = True
        print(f'{parkingtUrl} → save_button.click(success)')
    else:
        print(f'{parkingtUrl} → save_button.click(failed)')
    return success

def telno_action(driver, txt):
    telnoText = telno(txt)
    telnoText = telnoText.replace('-', '')

    save_action(driver, telnoText)
    success = True

    print(f'TELNO: {telnoText} → save_button.click(success)')
    return success

def save_action(driver, answer):
    searchAnswer = driver.find_element(By.ID, 'searchAnswer')
    searchAnswer.send_keys(answer)
    saveBtn = driver.find_element(By.ID, 'saveBtn')
    saveBtn.click()

@app.command()
def code(idx: int, id: str, filter = typer.Argument("100")):
    driver = create_mobile_driver()
    retCode = code_internal(driver, idx, id, filter)
    driver.quit()
    return retCode

def code_internal(driver, idx: int, id: str, filter: str, quisConsonants=typer.Argument("")):
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

# 명소 
@app.command()
def place(idx: int, filter: str = typer.Argument("100"), q: str = typer.Argument(""), quistext: str = typer.Argument("")):
    clipboard_use = False
    placeName = None

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    driver = create_mobile_driver()
    url = search_naver(driver, q)

    print(f'place url: {url}')

    placeName = ''
    if 'http' in url:
        place = getPlaceCode(url)
        print(f'place: {place}')

        if place:
            placeName = code_internal(driver, idx, place, filter, quistext)
            if clipboard_use: 
                print(f'placeName: {placeName} → clipboard.copy')
                clipboard.copy(placeName)

    driver.quit()
    return placeName


@app.command()
def telno(q: str = typer.Argument("")):
    clipboard_use = False

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    driver = create_mobile_driver()
    url = search_naver(driver, q)

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

@app.command()
def home(q: str = typer.Argument("")):
    home_impl(q)

@app.command()
def fav(q: str = typer.Argument("")):
    home_impl(q, True)

def home_impl(q: str, fav: bool = False):
    clipboard_use = False

    if not q:
        q = clipboard.paste()
        clipboard_use = True

    driver = create_mobile_driver()
    url = search_naver(driver, q)

    print(f'place url: {url}')

    if 'http' in url:
        driver.get(url)
        try:
            homeUrl = driver.current_url
            print(f'HOME: {homeUrl}')

            favUrl = replaceHomeUrl(homeUrl)
            print(f'FAV: {favUrl}')
            print()

            if clipboard_use:
                if fav:
                    print(f'FAV: {favUrl} → clipboard.copy')
                    clipboard.copy(favUrl)
                else:
                    print(f'HOME: {homeUrl} → clipboard.copy')
                    clipboard.copy(homeUrl)
        except:
            print('NOT FOUND')

    driver.quit()

@app.command()
def info(q: str = typer.Argument("")):
    if not q:
        q = clipboard.paste()

    driver = create_mobile_driver()
    url = search_naver(driver, q)

    print(f'place url: {url}')

    if 'http' in url:
        place = getPlaceCode(url)
        print(f'place: {place}')

        url = f'https://m.place.naver.com/restaurant/{place}/information?entry=pll'
        driver.get(url)

        try:
            ninfo = driver.find_element(By.CSS_SELECTOR, '.T8RFa')
            infoText = ninfo.text

            infoTexts = infoText.split('\n')
            for t in infoTexts:
                print(t)
                print(extract_consonants(t))

            # print(f'infoText: {infoText}')
        except:
            print('NOT FOUND')

    driver.quit()


def getPlaceCode(url: str):
    match = re.search(r'/(?:place|restaurant|hairshop)/(\d+)', url)
    place = None
    if match:
        place = match.group(1)
    return place

def replaceHomeUrl(url: str):
    r = re.sub(r'\?.*$', '?from=search', url)
    return r


if __name__ == "__main__":
    app()
