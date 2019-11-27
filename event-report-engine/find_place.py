import json
import logging
import os
import time

import redis
import yaml

import googlemaps

with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

place_config = config.get('place')
redis_config = config.get('redis')
redis_key = redis_config.get('key')

MAPS_API_KEY = place_config.get("MAPS_API_KEY")

POS_LIST_KEY = redis_key.get('pos-tagger')
PLACE_LIST_KEY = redis_key.get('place')

SLEEP_DURATION = place_config.get('SLEEP_DURATION')

db = redis.Redis(
    decode_responses=True, 
    host=redis_config['host'], 
    port=redis_config['port']
)

gmaps = googlemaps.Client(key=MAPS_API_KEY)
logger = logging.getLogger(__name__)

def find_place(query):
    name = None
    address = None
    latitude = None
    longitude = None
    place_result = gmaps.find_place(input=query, input_type="textquery", 
                                    fields=['geometry', 'name', 'place_id', 'formatted_address'],
                                    location_bias="circle:100@-7.279268,112.797217")
    if len(place_result['candidates']) == 0:
        return name, address, latitude, longitude
    
    name = place_result['candidates'][0]['name']
    address = place_result['candidates'][0]['formatted_address']
    latitude = place_result['candidates'][0]['geometry']['location']['lat']
    longitude = place_result['candidates'][0]['geometry']['location']['lng']

    return name, address, latitude, longitude

if __name__ == "__main__":
    log_dir = os.path.join("storage", "place.log")
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_dir)

    formatter = logging.Formatter('%(asctime)s - FIND PLACE - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    logger.info("Start")

    while True:
        try:
            data = db.rpop(POS_LIST_KEY)
            if data is None:
                time.sleep(SLEEP_DURATION)
                continue

            data = json.loads(data)
            logger.info("Processing %s", data)

            if((data['loc'] == "") or (data['loc'] is None)):
                logger.info("Place is empty")
                continue
            else:
                name, address, latitude, longitude = find_place(data['loc'])
                
                data['place_name'] = name
                data['address'] = address
                data['latitude'] = latitude
                data['longitude'] = longitude

                data = json.dumps(data)
                db.lpush(PLACE_LIST_KEY, data)
                logger.info(name)

        except KeyboardInterrupt:
            break
        except:
            logger.error("Exception occur", exc_info=True)