import atexit
import json
import logging
import os
import time
from datetime import datetime, timedelta

import mysql.connector
import redis
import yaml
from mysql.connector import Error

with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

store_config = config.get('store')
database_config = config.get('database')

redis_config = config.get('redis')
redis_key = redis_config.get('key')

PLACE_LIST_KEY = redis_key.get('place')
STORE_LIST_KEY = redis_key.get("store")
SLEEP_DURATION = store_config.get('SLEEP_DURATION')

db = redis.Redis(
    decode_responses=True, 
    host=redis_config['host'], 
    port=redis_config['port']
)

connection = mysql.connector.connect(
    host=database_config['host'],
    database=database_config['name'],
    user=database_config['user'],
    password=database_config['pass']
)

logger = logging.getLogger(__name__)

sql_insert_query = """ 
INSERT INTO tweet
(tweet_id, user_id, tweet, created_at, place, address, latitude, longitude)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

@atexit.register
def cleanup():
    logger.info("Exiting")
    if connection.is_connected():
        connection.close()

if __name__ == "__main__":
    log_dir = os.path.join("storage", "store.log")
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_dir)

    formatter = logging.Formatter('%(asctime)s - STORE - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    logger.info("Start")

    while True:
        try:
            cursor = None
            data = db.rpop(PLACE_LIST_KEY)
            if data is None:
                time.sleep(SLEEP_DURATION)
                continue

            data = json.loads(data)
            logger.info("Processing %s", data)
            
            # convert time from UTC to UTC+7
            date = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
            date = date + timedelta(hours=7)
            created_at = str(date)

            if((data["place_name"] == "") or (data["place_name"] is None)):
                continue
            
            tweet_id = data["tweet_id"]
            user_id = data["user_id"]
            tweet = data["text"]
            place = data["place_name"]
            address = data["address"]
            latitude = data["latitude"]
            longitude = data["longitude"]

            print(data)

            cursor = connection.cursor()
            insert_tuple = (tweet_id, user_id, tweet, created_at, place, address, latitude, longitude)
            result  = cursor.execute(sql_insert_query, insert_tuple)
            connection.commit()
            logger.info("Success")

        except mysql.connector.Error as error :
            connection.rollback()
            logger.warning("Rollback", exc_info=True)
        except KeyboardInterrupt:
            break
        except:
            logger.error("Exception occur", exc_info=True)
        finally:
            #closing cursor
            if connection.is_connected() and cursor is not None:
                cursor.close()
