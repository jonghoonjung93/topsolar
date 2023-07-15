from imap_tools import MailBox
from account import *
from bs4 import BeautifulSoup
import re

with MailBox("imap.gmail.com", 993).login(EMAIL_ADDRESS, EMAIL_PASSWORD, initial_folder="INBOX") as mailbox:
    # 전체 메일 다 가져오기
    lists = []
    for msg in mailbox.fetch('(FROM kepco@kepco.co.kr)', limit=4, reverse=True):
        # print("[{}] {}".format(msg.from_, msg.subject))
        # print(msg.html)
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
        unit_price = tables[5].find_all('tr')[3].find_all('td')[0].text.replace("/kWh","")
        # print(f"기준단가({unit_price}), ", end="")

        #----------- 정산금액 가져오기 -----------
        price = tables[5].find_all('tr')[8].find_all('td')[4].text.replace("\t","").replace("\n","").replace("(⑧+⑪)","")
        # print(f"공급가액({price})")

        result_text = f"{power_plant_name} : 발전량({total}), 기준단가({unit_price}), 공급가액({price})"
        lists.append(result_text)
    
    # print(sorted(lists))
    for list in sorted(lists):
        print(list)
