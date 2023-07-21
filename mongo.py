from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from log_util import logger
from config_util import config
from datetime import datetime
from bson import ObjectId

uri = config.get("MongoDB", "endpoint")
client = MongoClient(uri)

class DB:

    def ping(self):
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def insert(self, url, title, price):
        try:
            db = client["gunddb"]
            collection = db["items"]
        
            current_time = datetime.now()
            alert_flag = False

            data = {
                "url": url,
                "title": title,
                "price": price,
                "alert_flag": alert_flag,
                "reg_dttm": current_time
            }

            collection.insert_one(data)

        except Exception as e:
            logger.error(e)
        

    def select(self):
        try:
            db = client["gunddb"]
            collection = db["items"]

            results = collection.find().sort("reg_dttm", -1)

            result_dict = []
            for row in results:
                result_dict.append({"id": str(row["_id"]), "url": row["url"], "title": row["title"], "price": row["price"]})

            return result_dict

        except Exception as e:
            logger.error(e)


    def dupCheck(self, url):
        try:
            db = client["gunddb"]
            collection = db["items"]

            results = collection.find_one({"url": url})

            if results:
                return True
            else:
                return False

        except Exception as e:
            logger.error(e)


    def selectByAlertFlag(self):
        try:
            db = client["gunddb"]
            collection = db["items"]

            condition = {"alert_flag": False}
            results = collection.find(condition)

            result_list = []
            for row in results:
                result_list.append([str(row["_id"]), row["url"], row["title"], row["price"]])

            return result_list

        except Exception as e:
            logger.error(e)


    def updateAlertFlag(self):
        try:
            db = client["gunddb"]
            collection = db["items"]

            condition = {"alert_flag": False}
            new_values = {"$set": {"alert_flag": True}}
            
            result = collection.update_many(condition, new_values)

            return result.modified_count

        except Exception as e:
            logger.error(e)


    def deleteById(self, id):
        try:
            db = client["gunddb"]
            collection = db["items"]

            condition = {"_id": ObjectId(id)}
            result = collection.delete_many(condition)

            logger.debug(result.deleted_count)
            return result.deleted_count

        except Exception as e:
            logger.error(e)


    def deleteAll(self):
        try:
            db = client["gunddb"]
            collection = db["items"]

            condition = {}
            result = collection.delete_many(condition)

            return result.deleted_count

        except Exception as e:
            logger.error(e)


if __name__ =="__main__":

    db = DB()
    db.ping()
    # db.insert("1.com", "aaa", 5000)
    # db.insert("2.com", "bbb", 6000)
    # db.insert("3.com", "ccc", 7000)
    print(db.select())
    # print(db.selectByAlertFlag())
    # print(db.dupCheck("1.com"))
    # print(db.dupCheck("5.com"))
    # db.updateAlertFlag()
    # db.deleteById('64ba917c6ed427e3c478ea29')
    # db.deleteAll()
