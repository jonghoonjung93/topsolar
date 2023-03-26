from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
#from webdriver_manager.chrome import ChromeDriverManager
from requests import Session
import time
import json

def fetch_today():
    options = Options()
    options.add_argument("headless") #크롬창이 뜨지 않고 백그라운드로 동작됨
    
    # config.json 파일처리 ----------------
    with open('config.json','r') as f:
        config = json.load(f)
    url = config['DEFAULT']['URL']
    user_id = config['DEFAULT']['ID']
    password = config['DEFAULT']['PASSWORD']
    # ------------------------------------

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    #driver.maximize_window()
    action = ActionChains(driver)

    #driver.find_element('id', 'user-id').click()
    #action.send_keys('ys3_8862').perform()
    driver.find_element(By.ID, "user-id").send_keys(user_id)

    #driver.find_element('id', 'user-password').click()
    #action.send_keys('1234').perform()
    driver.find_element(By.ID, "user-password").send_keys(password)

    #driver.find_element('id', 'login-btn').click()
    driver.find_element(By.ID, 'login-btn').click()
    """
    driver.find_element(By.CSS_SELETOR, "#id이름")
    driver.find_element(By.CSS_SELETOR, ".class이름")
    driver.find_element(By.CSS_SELETOR, "[title='title내용']")
    driver.find_element(By.LINK_TEXT, "어쩌구").click()
    driver.find_element(By.PARTIAL_LINK_TEXT, "쩌구").click()
    driver.find_elements(By.TAG_NAME, "span")
    < XPath 사용법 >
        크롬에서 검사한 html코드에서 마우스오른쪽 복사->XPath복사하면 아래값이 나옴
        //*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td
        driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td')
    """
    time.sleep(1) #대기시간이 없으면 로그인하기 전 페이지에서 작업이 됨
    """
    * 2번째 대기방법
        driver.implicitly_wait(10)
          ==> 10초까지 기다림. 대신 10초안에 웹화면이 표시되면 바로 진행되지만 안되는 경우 있음
    * 3번째 대기방법 (예를들면, 특정 버튼이 뜰때까지 기다리기)
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#search_btn')))
        button.click()
    """

    #print(driver.current_url) #로그인후 url 확인

    soup = BeautifulSoup(driver.page_source, "html.parser")
    #data = driver.find_element('id', 'app').text
    #day_data = soup.find('td').text
    
    today_kWh = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
    today_hour = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
    month_kWh = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
    result = {
        'today_kWh' : today_kWh,
        'today_hour' : today_hour,
        'month_kWh' : month_kWh
    }

    driver.quit()
    return result

    #time.sleep(100)

if __name__ == "__main__":
    result=fetch_today()
    print(result)


"""
driver.get('http://어쩌구저쩌구') #페이지 이동
time.sleep(1)
driver.find_element(By.CSS_SELETOR, '.class이름').click()
time.sleep(1)
action.send_keys('입력값').key_down(Keys.TAB).key_down(Keys.TAB).send_keys('다른입력값')
  --> SHIFT를 누르고 뭔가할때는 key_down(Keys.SHIFT).send_keys('어쩌구').key_up('Keys.SHIFT)
send_button = driver.find_element(By.CSS_SELECTOR, ".class이름") #버튼이동위해 위치 찾기

* 여러번 action.send_key를 하면 입력값이 초기화가 안되는 경우가 있음. 그럴때는
   action.reset_actions() 
* action이 너무 길어지면 괄호로 처리함
  (
    action.send_keys('입력값').key_down(Keys.TAB)
    .key_down(Keys.TAB).key_down(Keys.ENTER).pause(2) #중간에 2초쉬게할수있음
    .send_keys('다른입력값')
    .move_to_element(send_button).click() #이렇게 하면 아무거나 클릭할수 있음
    .perform()
  )
"""