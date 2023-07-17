from imap_tools import MailBox
from account import *
from bs4 import BeautifulSoup
import re
import pickle

# --------- gmail 에서 한전 이메일을 읽고, list 변수로 만들어서 파일로 저장해 놓는 프로그램 ----------- #

with MailBox("imap.gmail.com", 993).login(EMAIL_ADDRESS, EMAIL_PASSWORD, initial_folder="INBOX") as mailbox:
    # 전체 메일 다 가져오기
    lists = []
    dict_lists = []
    for msg in mailbox.fetch('(FROM kepco@kepco.co.kr)', limit=4, reverse=True):
        # print("[{}] {}".format(msg.from_, msg.subject))
        # print(msg.html)
        # msg_date = msg.date.strftime("%Y-%m-%d %H:%M:%S")
        msg_date = msg.date.strftime("%Y-%m-%d")
        soup = BeautifulSoup(msg.html, "html.parser")
        # title = soup.find('tbody').find('td')
        title = soup.find('strong')
        # print(title.text)

        tables = soup.find_all('table')
        # print(len(tables))

        #----------- 발전소명 가져오기 -----------
        # print(tables[1].td)
        table_text = tables[1].td.get_text().replace("\n","")
        # print(f"text = {table_text}")
        # pattern = r'발전소명 :\s+(.*?)\t'
        pattern = r'발전소명 :\s+(.*?)태양광발전소'
        match = re.search(pattern, table_text)
        # power_plant_name = match.group(1)
        # print("Power plant name:", power_plant_name)
        if match:
            power_plant_name = match.group(1).replace(" ","")
            # print(f"{power_plant_name} : ", end="")
        else:
            power_plant_name = "NoMatch"
            # print("No match found.")

        #----------- 발전량 가져오기 -----------
        total = tables[2].td.find_all('tr')[1].find_all('td')[4].text
        # print(f"발전량({total}), ", end="")

        #----------- 기준단가 가져오기 -----------
        unit_price = tables[5].find_all('tr')[3].find_all('td')[0].text.replace("/kWh","").replace(" 원","")
        # print(f"기준단가({unit_price}), ", end="")

        #----------- 정산금액 가져오기 -----------
        price = tables[5].find_all('tr')[8].find_all('td')[4].text.replace("\t","").replace("\n","").replace("(⑧+⑪)","").replace(" 원","")
        # print(f"공급가액({price})")

        result_text = f"{power_plant_name}({msg_date}) : 발전량({total}), 단가({unit_price}), 금액({price})"
        lists.append(result_text)

        solar_dict = {
            "date" : msg_date,
            "power_plant" : power_plant_name,
            "production" : total,
            "unit_price" : unit_price,
            "price" : price
        }
        dict_lists.append(solar_dict)
    
def gmail_read_save():  # gmail 읽고 데이터를 파일로 저장해놓기
    # print(sorted(lists))
    for list in sorted(lists):
        print(list)

    sum = 0
    sorted_data = sorted(dict_lists, key=lambda x: x['power_plant'])
    for dict in sorted_data:
        print(dict)
        sum = sum + int(dict['price'])
    # print(sum)
    print(f"[총 수익금(세후)] : {sum:,} 원")

    with open(f'data/kepco_{msg_date}.pickle', 'wb') as file:
        pickle.dump(sorted_data, file)

def pickle_read(msg_date):   # 저장된 파일을 읽어오기
    with open(f'data/kepco_{msg_date}.pickle', 'rb') as file:
        loaded_lists = pickle.load(file)
    for list in loaded_lists:
        print(list)

gmail_read_save()  # gmail 읽고 데이터를 파일로 저장해놓기
print("-------------------------------------------------------------")
pickle_read('2023-07-14')   # 저장된 파일을 읽어오기