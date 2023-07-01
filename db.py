import psycopg2
import logging
import configparser
from datetime import datetime
from util import convertStringToNumber

config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(filename="gundalert.log", encoding="utf-8", level=logging.INFO)

class DB:

    def getConnection(self):
        return psycopg2.connect(user=config.get("DB", "user"),
                                    password=config.get("DB", "password"),
                                    host=config.get("DB", "host"),
                                    port=config.get("DB", "port"),
                                    database=config.get("DB", "database"))


    def insert(self, url, title, price):
        try:
            connection = self.getConnection()
            cursor = connection.cursor()

            query = "INSERT INTO gund_item (url, title, price, soup_count, reg_dttm) VALUES (%s,%s,%s,1,CURRENT_TIMESTAMP) ON CONFLICT (url) DO UPDATE SET soup_count = gund_item.soup_count + 1, mod_dttm = CURRENT_TIMESTAMP"
            record = (url, title, convertStringToNumber(price))
            cursor.execute(
                query, record)

            connection.commit()
            return cursor.rowcount

        except (Exception, psycopg2.Error) as error:
            logging.error("Failed to insert record into mobile table %s",error)

        finally:
            if connection:
                cursor.close()
                connection.close()
                logging.debug("PostgreSQL connection is closed")


    def select(self):
        try:
            connection = self.getConnection()
            cursor = connection.cursor()

            query = "SELECT * FROM gund_item"
            cursor.execute(query)

            return cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            logging.error("Failed to insert record into mobile table %s",error)

        finally:
            if connection:
                cursor.close()
                connection.close()
                logging.debug("PostgreSQL connection is closed")


    def selectByAlertFlag(self):
        try:
            connection = self.getConnection()
            cursor = connection.cursor()

            query = "SELECT * FROM gund_item WHERE alert_flag = 'false'"
            cursor.execute(query)

            return cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            logging.error("Failed to insert record into mobile table %s",error)

        finally:
            if connection:
                cursor.close()
                connection.close()
                logging.debug("PostgreSQL connection is closed")


if __name__ =="__main__":
    db = DB()
    db.insert("test.com", "test", 1000)
    db.select()