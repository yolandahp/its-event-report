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
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence

from keras.models import Sequential
from keras.layers import LSTM, GRU, Activation, Dense, Dropout, Input, Embedding, MaxPooling1D
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping

with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

event_config = config.get('event-classifier')
redis_config = config.get('redis')
redis_key = redis_config.get('key')

STREAM_LIST_KEY = redis_key.get('streamer')
EVENT_LIST_KEY = redis_key.get('event-classifier')

db = redis.Redis(
    decode_responses=True, 
    host=redis_config['host'], 
    port=redis_config['port']
)
logger = logging.getLogger(__name__)

SLEEP_DURATION = event_config.get('SLEEP_DURATION')

model_path = "model/weights-best.h5"
tokenizer_path = "model/tokenizer.pickle"
max_words = 3000
max_len = 50

def rnn_model():
    model = Sequential()
    
    model.add(Embedding(max_words, 32, input_length=max_len))
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(64))
    
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics = ['accuracy'])

    return model

if __name__ == "__main__":
    log_dir = os.path.join("storage", "event-classifier.log")
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_dir)

    formatter = logging.Formatter('%(asctime)s - EVENT CLASSIFIER - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    logger.info("Start")

    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
    
    model = rnn_model()
    model.load_weights(filepath=model_path)

    while True:
        try:
            data = db.rpop(STREAM_LIST_KEY)
            if data is None:
                time.sleep(SLEEP_DURATION)
                continue

            data = json.loads(data)
            logger.info("Processing %s", data)

            test_sequences = tokenizer.texts_to_sequences([data["clean_clf"]])
            test_sequences_matrix = sequence.pad_sequences(test_sequences, maxlen=max_len)
            
            y_pred = model.predict_classes(test_sequences_matrix)
            
            if(y_pred[0][0] != 1):
                logger.info("Bukan Event")
                continue
            else:
                data = json.dumps(data)
                db.lpush(EVENT_LIST_KEY, data)
                logger.info("Event")
        
        except KeyboardInterrupt:
            break
        except:
            logger.error("Exception occur", exc_info=True)




