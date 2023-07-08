import psycopg2
from psycopg2 import pool
from log_util import logger
from config_util import config
from datetime import datetime
from util import convertStringToNumber

connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1,
                                                maxconn=5,
                                                user=config.get("DB", "user"),
                                                password=config.get("DB", "password"),
                                                host=config.get("DB", "host"),
                                                port=config.get("DB", "port"),
                                                database=config.get("DB", "database"))

def getConnection():
    return connection_pool.getconn()

def releaseConnection(conn):
    connection_pool.putconn(conn)

class DB:

    def insert(self, url, title, price):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "INSERT INTO gund_item (url, title, price, soup_count, reg_dttm) VALUES (%s,%s,%s,1,CURRENT_TIMESTAMP) ON CONFLICT (url) DO UPDATE SET soup_count = gund_item.soup_count + 1, mod_dttm = CURRENT_TIMESTAMP"
            record = (url, title, convertStringToNumber(price))
            cursor.execute(
                query, record)

            connection.commit()
            return cursor.rowcount

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to insert %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")

    def select(self):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "SELECT * FROM gund_item"
            cursor.execute(query)

            return cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to select %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")

    def dupCheck(self, url):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "SELECT * FROM gund_item WHERE url = %s"
            cursor.execute(query, (url,))

            rows = cursor.fetchall()
            if (len(rows)) > 0:
                return True
            else:
                return False

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to dupCheck %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")

    def selectByAlertFlag(self):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "SELECT * FROM gund_item WHERE alert_flag = 'false'"
            cursor.execute(query)

            return cursor.fetchall()

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to selectByAlertFlag %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")


    def updateAlertFlag(self):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "UPDATE gund_item SET alert_flag = 'true', alert_dttm = CURRENT_TIMESTAMP WHERE alert_flag = 'false'"
            cursor.execute(query)

            connection.commit()
            return cursor.rowcount

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to updateAlertFlag %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")

    def deleteById(self, id):
        try:
            connection = getConnection()
            cursor = connection.cursor()

            query = "DELETE FROM gund_item WHERE id = %s"
            cursor.execute(query, (id,))

            connection.commit()
            return cursor.rowcount

        except (Exception, psycopg2.Error) as error:
            logger.error("Failed to deleteById %s",error)

        finally:
            if connection is not None:
                cursor.close()
                releaseConnection(connection)
                logger.debug("PostgreSQL connection is closed")


if __name__ =="__main__":
    db = DB()
    db.insert("test.com", "test", 1000)
    db.select()
