import schedule
import time
import logging
from soup import Soup

logging.basicConfig(filename="schedule.log", encoding="utf-8", level=logging.DEBUG)

def call_func():
    soup = Soup()
    soup.premiumBandaiSoup()
    soup.bnkrMallSearchSoup()
    soup.gundamBoomSoupPaging()

try:
    schedule.every(5).seconds.do(call_func)
    while True:
        schedule.run_pending()
        time.sleep(1)
except Exception as e:
    logging.error(traceback.print_exc())