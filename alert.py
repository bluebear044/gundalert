import logging
import traceback
import configparser
from db import DB
from util import sendEmail
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)

class Alert:

    def newItemAlert(self):
        try:
            db = DB()
            rows = db.selectByAlertFlag()

            if 0 < len(rows):
                message = ""
                for row in rows:
                    data = {
                        'url': row[1],
                        'title': row[2],
                        'price': row[3]
                    }
                    message += data['url'] + " " + data['title'] + " " + str(data['price']) + "\n"

                sendEmail(config.get("Email", "sender"), config.get("Email", "password"), config.get("Email", "receiver"), "gundalert : " + datetime.now().strftime("%Y%m%d%H%M%S"), message)
                db.updateAlertFlag()
                logging.info("SEND EMAIL : It has been Sent.")
            else:
                logging.info("SEND EMAIL : Nothing happened.")
                

        except Exception as e:
            logging.error(traceback.print_exc())

if __name__ =="__main__":
    alert = Alert()
    alert.newItemAlert()