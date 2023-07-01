import logging
import traceback
from db import DB

class Alert:

    logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)

    def newItemAlert(self):
        try:
            db = DB()
            rows = db.selectByAlertFlag()
            for item in rows: 
                logging.info(item)
            
        except Exception as e:
            logging.error(traceback.print_exc())

if __name__ =="__main__":
    alert = Alert()
    alert.newItemAlert()