import schedule
import time
from alert import Alert

def call_func():
    alert = Alert()
    alert.newItemAlert()

schedule.every(5).seconds.do(call_func)

while True:
    schedule.run_pending()
    time.sleep(1)
