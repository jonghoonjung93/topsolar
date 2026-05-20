from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from requests import Session
import requests
from selenium.webdriver.support.select import Select
import time, datetime
import json
import telegram
import asyncio
import sqlite3
import socket
import os
import sys

def mode_check():
  hostname = socket.gethostname()
  # print("hostname = " + hostname)
  if 'local' in hostname.lower(): # jungui-MacBookAir.local, Mac-mini.local
    MODE = "TEST"
  else:
    MODE = "ONLINE" # ubuntu-online
  return(MODE)

def printL(message):	# 로그파일 기록 함수 (맥북에서는 화면에도 출력)
	log_directory = "logs"
	current_date = datetime.datetime.now().strftime("%Y%m%d")
	log_path = os.path.join(log_directory, f"log.{current_date}")
	current_time = datetime.datetime.now()
	formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

	if mode_check() == 'TEST':
		print(message)
	with open(log_path, "a") as log_file:
		log_file.write(f"{formatted_time} {message}\n")

def fetch_today():
    result = mode_check()
    # print(result)

    options = Options()
    if result == "ONLINE":
      # options.add_argument("headless") # ONLINE 에서만 크롬창이 뜨지 않고 백그라운드로 동작됨
      options.add_argument("--headless=new")

    # 아래는 가끔 작업이 실패하는걸 개선하기 위해 추가함 (20260414)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")

    # 수정목표.
    # 로그인 먼저하고, 값이 없으면 몇초 대기후 다시 보고.. 이런거 반복하는 방식 개선 필요함.
    
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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 사이트 접속 및 로그인
    # driver.get(url)
    for i in range(3):
        try:
            driver.get(url)
            break
        except:
            driver.quit()
            driver = webdriver.Chrome(options=options)

    time.sleep(5)
    driver.find_element(By.ID, "user-id").send_keys(user_id)
    driver.find_element(By.ID, "user-password").send_keys(password)
    driver.find_element(By.ID, 'login-btn').click()
    time.sleep(5)

    solars = ['Table_94','Table_95','Table_117','Table_118']
    today_kWh = ['','','','']
    today_hour = ['','','','']
    month_kWh = ['','','','']

    WAIT_TIME = 5
    WAIT_CNT = 100

    for i, table in enumerate(solars):
      for retry in range(5): # 수치가 0일 경우 최대 5번까지 반복
        # print(f"solars[{i}]: {table}")

        # 와이솔라1호~4호 선택
        select = Select(driver.find_element(By.CLASS_NAME, 'form-select'))
        select.select_by_value(table)
        # print("wait... 10sec")
        count = 0
        while count < WAIT_CNT:
          time.sleep(WAIT_TIME) #몇 kWh 가 생산되었는지 표시되기까지 기다리는 시간
        
          today_kWh[i] = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[1]/td').text
          today_hour[i] = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[2]/td').text
          month_kWh[i] = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/table/tbody/tr[3]/td').text
          # print(f"today_kWh[{i}] (count={str(count)})")
          count += 1
          if today_kWh[i] == '':  # today_kW1 데이타가 null 이면 while 문을 다시 시도
            # print(f"wait... 10sec {count}")
            continue
          else: # 결과값 찾기에 성공했을때는 break 로 while 문 탈출
            # 수치가 0일 경우 재작업 로직 (단, count가 WAIT_CNT에 도달하기 전이라도 0이면 재시도 대상)
            if today_kWh[i] == '0' or today_kWh[i] == '0.0':
              printL(f"와이솔라{i+1}호 : {today_kWh[i]} 수치 0 감지. 5초 후 로그인부터 재시도 (시도 {retry+1}/5)")
              time.sleep(5)
              
              # 로그인부터 다시 수행
              driver.get(url)
              time.sleep(5)
              driver.find_element(By.ID, "user-id").clear()
              driver.find_element(By.ID, "user-id").send_keys(user_id)
              driver.find_element(By.ID, "user-password").clear()
              driver.find_element(By.ID, "user-password").send_keys(password)
              driver.find_element(By.ID, 'login-btn').click()
              time.sleep(5)
              break # while 문 탈출하여 retry 루프의 다음 시도로 이동
            
            printL(f"와이솔라{i+1}호 : {today_kWh[i]} 재시도 {count}회")
            break # while 문 탈출
        
        # while 문을 정상적으로 마쳤고 수치가 0이 아니면 retry 루프 탈출
        if today_kWh[i] != '' and today_kWh[i] != '0' and today_kWh[i] != '0.0':
          break
        # 만약 5번 시도했는데도 계속 0이면 그냥 다음 발전소로 진행 (무한루프 방지)
        if retry == 4:
          printL(f"와이솔라{i+1}호 : 5회 시도 후에도 수치 0. 다음으로 진행.")
          break
    
    result = {
        'today_kWh': today_kWh,
        'today_hour': today_hour,
        'month_kWh': month_kWh
    }
    
    driver.quit()

    # print(result['today_kWh'], result['month_kWh'])

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_date = current_time.strftime("%Y%m%d")
    formatted_month = current_time.strftime("%Y%m")

    # DB insert 처리
    try:
      conn = sqlite3.connect('topsolar.sqlite3')
      cursor = conn.cursor()

      data_list1 = [
        (formatted_date, 'ysolar1', today_kWh[0], today_hour[0]),
        (formatted_date, 'ysolar2', today_kWh[1], today_hour[1]),
        (formatted_date, 'ysolar3', today_kWh[2], today_hour[2]),
        (formatted_date, 'ysolar4', today_kWh[3], today_hour[3])
      ]
      data_list2 = [
        (formatted_month, 'ysolar1', month_kWh[0]),
        (formatted_month, 'ysolar2', month_kWh[1]),
        (formatted_month, 'ysolar3', month_kWh[2]),
        (formatted_month, 'ysolar4', month_kWh[3])
      ]
      cursor.executemany("INSERT OR REPLACE INTO power_gen_day (date, st_name, gen_kWh, gen_hour) VALUES (?,?,?,?);", data_list1)
      cursor.executemany("INSERT OR REPLACE INTO power_gen_month (month, st_name, gen_kWh) VALUES (?,?,?);", data_list2)

      conn.commit()
    finally:
      conn.close()


    # telegram 메세지 발송
    async def tele_push(content): #텔레그램 발송용 함수
      bot = telegram.Bot(token = token)
      await bot.send_message(chat_id, formatted_time + "\n" + content, parse_mode = 'Markdown')
    
    # msg_content = str(result)
    msg_content = "*<탑솔라 당일>\n" + str(result['today_kWh']) + "*\n<탑솔라 당월>\n[" + str(result['month_kWh']) + "]"
    
    # 발전량 수치 차이 체크 (20% 이상 차이 확인)
    is_anomaly = False
    try:
        vals = [float(x) for x in today_kWh if x]
        if len(vals) > 0:
            max_val = max(vals)
            min_val = min(vals)
            if max_val > 0 and (max_val - min_val) / max_val > 0.2 and (max_val - min_val) > 20:
                is_anomaly = True
                printL(f"[TOPSOLAR] 수치 이상 감지: {min_val} vs {max_val} (20% 초과 차이 및 절대차이 20 초과)")
    except Exception as e:
        printL(f"[TOPSOLAR] 수치 체크 오류: {e}")

    if "notele" not in sys.argv or is_anomaly:
      asyncio.run(tele_push(msg_content)) #텔레그램 발송 (asyncio를 이용해야 함)

    return result

def fetch_today_kp():
  result = mode_check()
  # print(result)

  options = Options()
  if result == "ONLINE":
    options.add_argument("headless") # ONLINE 에서만 크롬창이 뜨지 않고 백그라운드로 동작됨

  # 수정목표.
  # 로그인 먼저하고, 값이 없으면 몇초 대기후 다시 보고.. 이런거 반복하는 방식 개선 필요함.
  
  # config.json 파일처리 ----------------
  with open('config.json','r') as f:
      config = json.load(f)
  url1 = config['DEFAULT']['URL_KP']  # 로그인 페이지
  url2 = config['DEFAULT']['URL_KP_TIME'] # 시간대별 사용량 조회 페이지
  url3 = config['DEFAULT']['URL_KP_DAYLY'] # 일별 사용량 조회 페이지
  user_id = config['DEFAULT']['YSOLAR_ID']
  password = config['DEFAULT']['YSOLAR_PW']
  token = config['DEFAULT']['TOKEN']
  chat_id = config['DEFAULT']['CHAT-ID']
  # ------------------------------------
  # print(user_id)
  # print(password)
  # print(url1)
  
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service, options=options)
  # Set browser window size to maximum
  # driver.maximize_window()

  today_kWh = ['','','','']
  today_hour = ['','','','']
  month_kWh = ['','','','']

  for i, ysolar in enumerate(user_id):
    for retry in range(5): # 수치가 0일 경우 최대 5번까지 반복
      # 사이트 접속 및 로그인
      driver.get(url1)
      time.sleep(4)
      try:
        driver.find_element(By.CLASS_NAME, "popclose").click()
        printL("popclose click")
      except:
        printL("popclose not found")

      try:
        driver.find_element(By.ID, "RSA_USER_ID").send_keys(user_id[i])
        driver.find_element(By.ID, "RSA_USER_PWD").send_keys(password)
        # 아래 3가지 로그인버튼 클릭 방법중 한개만 온라인에서 성공함 (개발에서는 다 성공)
        driver.find_element(By.ID, "RSA_USER_PWD").send_keys(Keys.ENTER)
        # driver.find_element(By.CLASS_NAME, 'intro_btn').click()
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/form/fieldset/input[1]").click()
      except:
        printL("로그인 실패. 재시도(1회만)")
        try:
          driver.get(url1)
          time.sleep(10)
          driver.find_element(By.ID, "RSA_USER_ID").send_keys(user_id[i])
          driver.find_element(By.ID, "RSA_USER_PWD").send_keys(password)
          driver.find_element(By.ID, "RSA_USER_PWD").send_keys(Keys.ENTER)
        except:
          printL("로그인 실패. 2회 실패. return")
          result = {
              'today_kWh': today_kWh,
              'month_kWh': month_kWh
          }
          return result
      
      time.sleep(1)
      driver.get(url2)  # 시간대별 사용량 조회 페이지 이동 (당일자 조회용)
      time.sleep(5)
      # 발전 라디오 버튼 클릭
      try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[1]/input[6]").click()
      except:
        printL("발전 라디오 버튼 클릭 실패1")
        time.sleep(3)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[1]/input[6]").click()
      time.sleep(1)
      # 조회 버튼 클릭
      # driver.find_element(By.CLASS_NAME, "btn_blue_right").click()  #이거는 실패, XPATH로 변경
      try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[2]/span[1]/a").click()
      except:
        printL("조회 버튼 클릭 실패")
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[2]/span[1]/a").click()
      time.sleep(1)
      # 당일 발전량 가져오기
      today_kWh[i] = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[5]/table/tbody/tr[1]/td[6]").text
      # 소수점 1자리까지만 표시하는걸로 변환 (원래 소수점 3자리로 나옴)
      today_kWh[i] = "{:.1f}".format(float(today_kWh[i]))
      printL(f"[한전] 와이솔라{i+1}호: {today_kWh[i]}")
      
      # 수치가 0일 경우 재작업 로직
      if float(today_kWh[i]) == 0:
        printL(f"[한전] 와이솔라{i+1}호: 수치 0 감지. 5초 후 로그인부터 재시도 (시도 {retry+1}/5)")
        time.sleep(5)
        if retry < 4:
          continue # 다시 로그인부터 수행
      
      time.sleep(1)

      driver.get(url3)  # 일별 사용량 조회 페이지 이동 (월간 합계 조회용)
      time.sleep(5)
      # 발전 라디오 버튼 클릭
      try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[1]/input[4]").click()
      except:
        printL("발전 라디오 버튼 클릭 실패2")
        time.sleep(3)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[1]/input[4]").click()
      # 조회 버튼 클릭
      time.sleep(1)
      # driver.find_element(By.CLASS_NAME, "btn_blue_right").click()
      try:
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[2]/span[1]/a").click()
      except:
        printL("조회 버튼 클릭 실패")
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/p[2]/span[1]/a").click()
      time.sleep(1)
      # 당월 총발전량 가져오기 (소수점 아래는 버림)
      month_kWh[i] = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[5]/table/tbody/tr/td[4]").text.split('.')[0]
      printL(f"[한전] 와이솔라{i+1}호 month: {month_kWh[i]}")
      time.sleep(2)

      # logout 버튼 클릭
      driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/p/a[2]").click()
      time.sleep(2)
      break # 성공했으므로 retry 루프 탈출
  # printL(f"[한전] 당일 발전량: {today_kWh}")
  # printL(f"[한전] 당월 발전량: {month_kWh}")
  
  result = {
      'today_kWh': today_kWh,
      'month_kWh': month_kWh
  }
  
  driver.quit()

  printL(f"{result['today_kWh']}, {result['month_kWh']}")

  current_time = datetime.datetime.now()
  formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
  formatted_date = current_time.strftime("%Y%m%d")
  formatted_month = current_time.strftime("%Y%m")

  flag = False
  if flag:
    # DB insert 처리
    try:
      conn = sqlite3.connect('topsolar.sqlite3')
      cursor = conn.cursor()

      data_list1 = [
        (formatted_date, 'ysolar1', today_kWh[0], today_hour[0]),
        (formatted_date, 'ysolar2', today_kWh[1], today_hour[1]),
        (formatted_date, 'ysolar3', today_kWh[2], today_hour[2]),
        (formatted_date, 'ysolar4', today_kWh[3], today_hour[3])
      ]
      data_list2 = [
        (formatted_month, 'ysolar1', month_kWh[0]),
        (formatted_month, 'ysolar2', month_kWh[1]),
        (formatted_month, 'ysolar3', month_kWh[2]),
        (formatted_month, 'ysolar4', month_kWh[3])
      ]
      cursor.executemany("INSERT OR REPLACE INTO power_gen_day (date, st_name, gen_kWh, gen_hour) VALUES (?,?,?,?);", data_list1)
      cursor.executemany("INSERT OR REPLACE INTO power_gen_month (month, st_name, gen_kWh) VALUES (?,?,?);", data_list2)

      conn.commit()
    finally:
      conn.close()

  # smp 수익 계산 로직
  flag = True
  if flag:
    total_kWh = sum(float(x) for x in today_kWh if x)

    # smp 당일 단가 조회
    try:
        with open('../attendance/today_smp.txt', 'r', encoding='utf-8') as f:
            today_smp = f.read().strip()
        # txt 파일에 기록된 값이 숫자인지 확인
        today_smp = float(today_smp)
        printL(f"[한전] 당일 smp 단가: {today_smp}")
    except (FileNotFoundError, ValueError) as e:
        printL(f"smp 단가 파일 읽기 실패: {e}")
        today_smp = 100  # 기본값

    smp_income = total_kWh * today_smp
    smp_income = int(total_kWh * today_smp)  # 소수점 아래 버림
    smp_income_str = "{:,}".format(smp_income)  # 3자리마다 콤마 추가
    printL(f"[한전] 당일 smp 수익: {smp_income}")

    # rec 당일 단가 조회
    try:
        with open('../attendance/today_rec.txt', 'r', encoding='utf-8') as f:
            today_rec = f.read().strip()
        # txt 파일에 기록된 값이 숫자인지 확인
        today_rec = float(today_rec)
        printL(f"[한전] 당일 rec 단가: {today_rec}")
    except (FileNotFoundError, ValueError) as e:
        printL(f"rec 단가 파일 읽기 실패: {e}")
        today_rec = 70000  # 기본값

    # rec 수익 계산 로직
    rec_count = f"{round(total_kWh / 1000 * 1.1, 1):.1f}"  # 소수점 한자리 아래 버림
    printL(f"[한전] 당일 rec 개수: {rec_count}")
    rec_income = int(float(rec_count) * float(today_rec))
    rec_income_str = "{:,}".format(rec_income)  # 3자리마다 콤마 추가
    printL(f"[한전] 당일 rec 수익: {rec_count}, {rec_income_str}")
    total_income = smp_income + rec_income
    total_income_str = "{:,}".format(total_income)  # 3자리마다 콤마 추가
    printL(f"[한전] 당일 총 수익: {total_income_str}")

  # 제주 날씨 체크
  flag = True
  if flag:
      try:
          # 제주 조천읍 날씨 정보 가져오기 (네이버 통합검색이 크롤링에 더 용이함)
          weather_url = "https://search.naver.com/search.naver?query=제주조천읍날씨"
          headers = {"User-Agent": "Mozilla/5.0"}
          response = requests.get(weather_url, headers=headers)
          soup = BeautifulSoup(response.text, 'html.parser')

          # 현재 온도 (현재 온도 12.9° -> 12.9°)
          temp_el = soup.select_one('.temperature_text strong')
          current_temp = temp_el.text.replace('현재 온도', '').strip() if temp_el else '정보없음'
          
          # 날씨 상태
          condition_el = soup.select_one('.before_slash') or soup.select_one('.weather_main .summary .weather') or soup.select_one('.weather_main .weather')
          weather_state = condition_el.text.strip() if condition_el else '정보없음'
          
          # 강수 확률
          rain_el = soup.select_one('.rain_rate .num') or soup.select_one('.list_area .rain_rate .num') or soup.select_one('.rainfall .num')
          rain_rate = rain_el.text.strip() if rain_el else '0%'

          # 내일 날씨 추출
          tomorrow_weather = {'temp_low': '', 'temp_high': '', 'am_cond': '', 'am_rain': '', 'pm_cond': '', 'pm_rain': ''}
          for li in soup.select('.week_item'):
              if '내일' in li.select_one('.day').text:
                  # 기온
                  tomorrow_weather['temp_low'] = li.select_one('.lowest').text.replace('최저기온', '').strip() if li.select_one('.lowest') else ''
                  tomorrow_weather['temp_high'] = li.select_one('.highest').text.replace('최고기온', '').strip() if li.select_one('.highest') else ''
                  
                  # 오전/오후 날씨 및 강수확률
                  weather_inners = li.select('.weather_inner')
                  if len(weather_inners) >= 2:
                      # 오전
                      tomorrow_weather['am_rain'] = weather_inners[0].select_one('.rainfall').text.strip() if weather_inners[0].select_one('.rainfall') else ''
                      tomorrow_weather['am_cond'] = weather_inners[0].select_one('.blind').text.strip() if weather_inners[0].select_one('.blind') else ''
                      # 오후
                      tomorrow_weather['pm_rain'] = weather_inners[1].select_one('.rainfall').text.strip() if weather_inners[1].select_one('.rainfall') else ''
                      tomorrow_weather['pm_cond'] = weather_inners[1].select_one('.blind').text.strip() if weather_inners[1].select_one('.blind') else ''
                  break

          # 변수에 저장
          jeju_weather = {
              'today': {
                  'temperature': current_temp,
                  'condition': weather_state,
                  'rain_chance': rain_rate
              },
              'tomorrow': tomorrow_weather
          }
          
          printL(f"[제주날씨] 오늘: {current_temp}, {weather_state}, 강수확률: {rain_rate}")
          printL(f"[제주날씨] 내일: {tomorrow_weather['temp_low']}~{tomorrow_weather['temp_high']}, 오전 {tomorrow_weather['am_cond']}({tomorrow_weather['am_rain']}), 오후 {tomorrow_weather['pm_cond']}({tomorrow_weather['pm_rain']})")
          
      except Exception as e:
          printL(f"[제주날씨] 오류: {e}")
          jeju_weather = {
              'today': {'temperature': '정보없음', 'condition': '정보없음', 'rain_chance': '정보없음'},
              'tomorrow': {'temp_low': '', 'temp_high': '', 'am_cond': '', 'am_rain': '', 'pm_cond': '', 'pm_rain': ''}
          }
 
  # telegram 메세지 발송
  async def tele_push(content): #텔레그램 발송용 함수
    bot = telegram.Bot(token = token)
    await bot.send_message(chat_id, formatted_time + "\n" + content, parse_mode = 'Markdown')
  
  # msg_content = str(result)
  # 텔레그램 메시지 구성
  weather_msg = f"[[제주날씨]] 오늘 {jeju_weather['today']['temperature']} {jeju_weather['today']['condition']} ({jeju_weather['today']['rain_chance']})"
  if jeju_weather['tomorrow']['temp_low']:
      weather_msg += f"\n[[내일]] {jeju_weather['tomorrow']['temp_low']} ~ {jeju_weather['tomorrow']['temp_high']} "
      weather_msg += f"오전 {jeju_weather['tomorrow']['am_cond']}({jeju_weather['tomorrow']['am_rain']}), "
      weather_msg += f"오후 {jeju_weather['tomorrow']['pm_cond']}({jeju_weather['tomorrow']['pm_rain']})"

  msg_content = f"*<한전 당일>*\n[{str(result['today_kWh'])}]\n<한전 당월>\n[{str(result['month_kWh'])}]\n\n<SMP> {str(today_smp)}원\nToday : {str(smp_income_str)}원 + REC: {rec_count}개, {rec_income_str}원\nTotal : {total_income_str}원\n\n{weather_msg}"
  
  # 발전량 수치 차이 체크 (20% 이상 차이 확인)
  is_anomaly = False
  try:
      vals = [float(x) for x in today_kWh if x]
      if len(vals) > 0:
          max_val = max(vals)
          min_val = min(vals)
          if max_val > 0 and (max_val - min_val) / max_val > 0.2 and (max_val - min_val) > 20:
              is_anomaly = True
              printL(f"[한전] 수치 이상 감지: {min_val} vs {max_val} (20% 초과 차이 및 절대차이 20 초과)")
  except Exception as e:
      printL(f"[한전] 수치 체크 오류: {e}")

  if "notele" not in sys.argv or is_anomaly:
    asyncio.run(tele_push(msg_content)) #텔레그램 발송 (asyncio를 이용해야 함)

  # 결과 데이터 JSON 파일로 저장
  result_data = {
      'timestamp': formatted_time,
      'today_kWh': result['today_kWh'],
      'month_kWh': result['month_kWh'],
      'smp_price': today_smp,
      'smp_income': smp_income,
      'rec_price': today_rec,
      'rec_count': rec_count,
      'rec_income': rec_income,
      'total_income': total_income,
      'weather': jeju_weather
  }
  
  with open('ysolar_result.json', 'w', encoding='utf-8') as f:
      json.dump(result_data, f, ensure_ascii=False, indent=4)
  printL("결과 데이터를 ysolar_result.json 파일로 저장하였습니다.")

  return result

if __name__ == "__main__":
  # 한전파워플래너 로직 실행
  flag = True
  if flag:
    printL("[한전] 실행")
    result2=fetch_today_kp()
    printL(result2)
    # Check if any value in today_kWh is empty
    if '' in result2['today_kWh']:
        printL("[KP] ERROR: One or more today_kWh values are missing")
        # 재시도
        result2=fetch_today_kp()
        printL(result2)

  # 탑솔라 로직 실행
  flag = False
  if flag:
    printL("[TOPSOLAR] 실행")
    result=fetch_today()
    printL(result)
    # Check if any value in today_kWh is empty
    if '' in result['today_kWh']:
        printL("[TOPSOLAR] ERROR: One or more today_kWh values are missing")
        # 재시도
        result=fetch_today()
        printL(result)

