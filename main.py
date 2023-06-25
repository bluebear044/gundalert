import schedule
import time
import datetime
import logging
import configparser
from soup import Soup
from util import sendEmail
from util import compareDictsArray
from util import sortDictsArray

config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)
org_data = []

def call_func():
    soup = Soup()
    soup.premiumBandaiSoup()
    # soup.bnkrMallSearchSoup()
    # soup.gundamBoomSoupPaging()

    new_data = soup.data_list
    global org_data

    sorted_org_data = sortDictsArray(org_data, 'url')
    sorted_new_data = sortDictsArray(new_data, 'url')

    diff_data = compareDictsArray(sorted_org_data, sorted_new_data)
    if 0 < len(diff_data):
        message = ""
        for item in diff_data:
            message += ' '.join(str(value) for value in item.values()) + "\n"
        logging.info("alert!")
        sendEmail(config.get("Email", "sender"), config.get("Email", "password"), config.get("Email", "receiver")
            , "gundalert : " + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            , message)
    else:
        logging.info("nothing happen")

    org_data = new_data
    soup.clear()


schedule.every(5).seconds.do(call_func)

while True:
    schedule.run_pending()
    time.sleep(1)
