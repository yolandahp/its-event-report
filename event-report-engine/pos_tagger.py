import json
import logging
import os
import time
import pickle

import warnings
warnings.filterwarnings("ignore")

import redis
import yaml

import numpy as np
import string
import re
import html

import nltk
from nltk.tokenize import word_tokenize

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

pos_config = config.get('pos-tagger')
redis_config = config.get('redis')
redis_key = redis_config.get('key')

EVENT_LIST_KEY = redis_key.get('event-classifier')
POS_LIST_KEY = redis_key.get('pos-tagger')

db = redis.Redis(
    decode_responses=True, 
    host=redis_config['host'], 
    port=redis_config['port']
)
logger = logging.getLogger(__name__)

SLEEP_DURATION = pos_config.get('SLEEP_DURATION')

file_tag = open('model/indonesian_ngram_pos_tag.pickle', 'rb')
ngram_tagger = pickle.load(file_tag)
file_tag.close()

isascii = lambda s: len(s) == len(s.encode())

def pos_tag(text):
    words = []
    tags = []
    
    res_tag = ngram_tagger.tag(word_tokenize(text))
    for x in res_tag:
        if x[0] in string.punctuation:
            words.append(x[0])
            tags.append('Z')
        elif not isascii(x[0]):
            words.append(x[0])
            tags.append('EMO')
        else:
            words.append(x[0])
            tags.append(x[1])
            
    return words, tags

places = []
with open('extra/Gazetteer.txt') as f:
    lines = f.readlines()
    for line in lines:
        places.append(line[:-1])

def match_gazetteer(text):
    place, score = process.extractOne(text, places, scorer=fuzz.token_sort_ratio)
    return score

def get_location(text):
    words, tags = pos_tag(text)
    idx_s = 0
    idx_e = 0
    
    place = ""
    cur_score = 0

    for i in range(len(tags)):
        if(tags[i] == 'NN' or tags[i] == 'NNP'):
            if(i == 0):
                idx_s = 0
                idx_e = 0
            elif(tags[i-1] == 'NN' or tags[i-1] == 'NNP'):
                idx_e = i
            else:
                idx_s = i
                idx_e = i
        elif(i != 0 and (tags[i-1] == 'NN' or tags[i-1] == 'NNP')):
            if(idx_e - idx_s + 1 > 1):
                query = ' '.join(words[idx_s:idx_e+1])
                score = match_gazetteer(query)
                if score > cur_score:
                    cur_score = score
                    place = query

        
        if((i == len(tags)-1) and (tags[i] == 'NN' or tags[i] == 'NNP')):
            if(idx_e - idx_s + 1 > 1):
                query = ' '.join(words[idx_s:idx_e+1])
                score = match_gazetteer(query)
                if score > cur_score:
                    cur_score = score
                    place = query
    
    return place

if __name__ == "__main__":
    log_dir = os.path.join("storage", "pos-tagger.log")
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_dir)

    formatter = logging.Formatter('%(asctime)s - POS TAGGER - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    logger.info("Start")

    while True:
        try:
            data = db.rpop(EVENT_LIST_KEY)
            if data is None:
                time.sleep(SLEEP_DURATION)
                continue

            data = json.loads(data)
            logger.info("Processing %s", data)

            place = get_location(data['clean_pos'])
            data['loc'] = place

            if(place == ""):
                logger.info("Place is empty")
                continue
            else:
                data = json.dumps(data)
                db.lpush(POS_LIST_KEY, data)
                logger.info(place)
        
        except KeyboardInterrupt:
            break
        except:
            logger.error("Exception occur", exc_info=True)