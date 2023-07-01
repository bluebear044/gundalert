import logging
import traceback
import configparser
from db import DB

class Alert:

    config = configparser.ConfigParser()
    config.read("config.ini")
    logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)

    def newItemAlert(self):
        try:
            db = DB()
            rows = db.selectByAlertFlag()
            for item in rows: 
                logging.info(item)

            # todo : alert_flag값이 false인 것 (알람이 필요한 것)에 대해 메일 전송 후 update_flag값 true로 업데이트하기
            # message += ' '.join(str(value) for value in item.values()) + "\n"
            # sendEmail(config.get("Email", "sender"), config.get("Email", "password"), config.get("Email", "receiver"), "gundalert : " + datetime.datetime.now().strftime("%Y%m%d%H%M%S"), message)
            
        except Exception as e:
            logging.error(traceback.print_exc())

if __name__ =="__main__":
    alert = Alert()
    alert.newItemAlert()