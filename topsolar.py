from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
#from webdriver_manager.chrome import ChromeDriverManager
from requests import Session
from selenium.webdriver.support.select import Select
import time, datetime
import json
import telegram
import asyncio

def fetch_today():
    options = Options()
    options.add_argument("headless") #크롬창이 뜨지 않고 백그라운드로 동작됨
    
    # config.json 파일처리 ----------------
    with open('config.json','r') as f:
        config = json.load(f)
    url = config['DEFAULT']['URL']
    user_id = config['DEFAULT']['ID']
    password = config['DEFAULT']['PASSWORD']
    token = config['DEFAULT']['TOKEN']
    chat_id = config['DEFAULT']['CHAT-ID']
    # ------------------------------------
    #print(user_id)
    #print(password)
    #print(url)

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    #driver.maximize_window()
    action = ActionChains(driver)

    time.sleep(3)
    driver.find_element(By.ID, "user-id").send_keys(user_id)
    driver.find_element(By.ID, "user-password").send_keys(password)
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

    # soup = BeautifulSoup(driver.page_source, "html.parser")

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

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    async def tele_push(content): #텔레그램 발송용 함수
      bot = telegram.Bot(token = token)
      await bot.send_message(chat_id, formatted_time + "\n" + content)
    
    msg_content = str(result)
    asyncio.run(tele_push(msg_content)) #텔레그램 발송 (asyncio를 이용해야 함)

    return result

def fetch_today2():
    options = Options()
    options.add_argument("headless") #크롬창이 뜨지 않고 백그라운드로 동작됨
    
    # config.json 파일처리 ----------------
    with open('config.json','r') as f:
        config = json.load(f)
    url = config['DEFAULT']['URL']
    user_id = config['DEFAULT']['ID']
    password = config['DEFAULT']['PASSWORD']
    token = config['DEFAULT']['TOKEN']
    chat_id = config['DEFAULT']['CHAT-ID']
    # ------------------------------------
    #print(user_id)
    #print(password)
    #print(url)

    driver = webdriver.Chrome(options=options)
    # driver.get(url)
    #driver.maximize_window()
    # action = ActionChains(driver)


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
    # time.sleep(2) #대기시간이 없으면 로그인하기 전 페이지에서 작업이 됨
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

    # soup = BeautifulSoup(driver.page_source, "html.parser")

    #data = driver.find_element('id', 'app').text
    #day_data = soup.find('td').text
    
    count = 0
    while count < 5:
      driver.get(url)
      time.sleep(3)
      driver.find_element(By.ID, "user-id").send_keys(user_id)
      driver.find_element(By.ID, "user-password").send_keys(password)
      driver.find_element(By.ID, 'login-btn').click()

      time.sleep(2) #대기시간이 없으면 로그인하기 전 페이지에서 작업이 됨

      # 와이솔라1호 (초기화면)
      today_kWh1 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
      today_hour1 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
      month_kWh1 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
      # print("today_kWh1 (" + str(count) + "): " + today_kWh1)
      count += 1
      if today_kWh1 != '':  # today_kW1 데이타가 null 이면 while 문을 다시 시도 (최대 5번만)
        break

    # 와이솔라2호 선택
    count = 0
    while count < 5:
      select = Select(driver.find_element(By.CLASS_NAME, 'form-select'))
      select.select_by_value('Table_95')

      time.sleep(2)
      today_kWh2 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
      today_hour2 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
      month_kWh2 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
      # print("today_kWh2 (" + str(count) + "): " + today_kWh2)
      count += 1
      if today_kWh2 != '':
        break

    # 와이솔라3호 선택
    count = 0
    while count < 5:
      select = Select(driver.find_element(By.CLASS_NAME, 'form-select'))
      select.select_by_value('Table_117')

      time.sleep(2)
      today_kWh3 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
      today_hour3 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
      month_kWh3 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
      # print("today_kWh3 (" + str(count) + "): " + today_kWh3)
      count += 1
      if today_kWh3 != '':
        break

    # 와이솔라4호 선택
    count = 0
    while count < 5:
      select = Select(driver.find_element(By.CLASS_NAME, 'form-select'))
      select.select_by_value('Table_118')

      time.sleep(2)
      today_kWh4 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
      today_hour4 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
      month_kWh4 = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
      # print("today_kWh4 (" + str(count) + "): " + today_kWh4)
      count += 1
      if today_kWh4 != '':
        break

    result = {
        'today_kWh' : [today_kWh1, today_kWh2, today_kWh3, today_kWh4],
        'today_hour' : [today_hour1, today_hour2, today_hour3, today_hour4],
        'month_kWh' : [month_kWh1, month_kWh2, month_kWh3, month_kWh4],
    }

    driver.quit()

    # print(result['today_kWh'], result['month_kWh'])

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # DB insert 처리


    # telegram 메세지 발송
    async def tele_push(content): #텔레그램 발송용 함수
      bot = telegram.Bot(token = token)
      await bot.send_message(chat_id, formatted_time + "\n" + content)
    
    # msg_content = str(result)
    msg_content = str(result['today_kWh']) + str(result['month_kWh'])
    asyncio.run(tele_push(msg_content)) #텔레그램 발송 (asyncio를 이용해야 함)

    return result

if __name__ == "__main__":
    # result=fetch_today()
    result=fetch_today2()
    print(result)
    # print(result['today_kWh'])
    # test_msg()
    # os.system("python3 ./telegram/telegram_push.py")


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
