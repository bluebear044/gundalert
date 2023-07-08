from log_util import logger
import traceback
from config_util import config
from db import DB
from util import sendEmail
from datetime import datetime

class Alert:

    def newItemAlert(self):
        try:
            db = DB()
            rows = db.selectByAlertFlag()

            if 0 < len(rows):
                message = "<html><body>"
                for row in rows:
                    data = {
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'price': row[3]
                    }
                    message += "<p>"
                    message += "<a href='" 
                    message += data['url']
                    message += "'>"
                    message += data['title']
                    message += "</a>"
                    message += " "
                    message += str(data['price'])
                    message += " "
                    message += "<a href='" 
                    message += config.get("Email", "apiUrl") + "/delete/" + str(data['id'])
                    message += "'>"
                    message += "재알림"
                    message += "</a>"
                    message += "</p>"

                message += "</body></html>"

                sendEmail(config.get("Email", "sender"), config.get("Email", "password"), config.get("Email", "receiver"), "gundalert : " + datetime.now().strftime("%Y%m%d%H%M%S"), message)
                db.updateAlertFlag()
                logger.info("SEND EMAIL : It has been Sent.")
            else:
                logger.info("SEND EMAIL : Nothing happened.")
                

        except Exception as e:
            logger.error(traceback.print_exc())

if __name__ =="__main__":
    alert = Alert()
    alert.newItemAlert()