import schedule
import time
from soup import Soup

def call_func():
    soup = Soup()
    soup.premiumBandaiSoup()
    soup.bnkrMallSearchSoup()
    soup.gundamBoomSoupPaging()

schedule.every(5).seconds.do(call_func)

while True:
    schedule.run_pending()
    time.sleep(1)
