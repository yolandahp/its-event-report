import json
import logging
import os
import time

import redis
import yaml

from cleaner import clean_proc_pos, clean_proc_clf
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

twitter_config = config.get('twitter')
redis_config = config.get('redis')
redis_key = redis_config.get('key')

APP_KEY = twitter_config.get('APP_KEY')
APP_SECRET = twitter_config.get('APP_SECRET')
OAUTH_TOKEN = twitter_config.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = twitter_config.get('OAUTH_TOKEN_SECRET')
TARGET_USER_ID = twitter_config.get('TARGET_USER_ID')

STREAM_LIST_KEY = redis_key.get('streamer')

db = redis.Redis(
    decode_responses=True, 
    host=redis_config['host'], 
    port=redis_config['port']
)
logger = logging.getLogger(__name__)


class CustomListener(StreamListener):
    def on_status(self, status):
        raw_tweet = None
        tweet_id = None
        user_id = None
        created_at = None
        if hasattr(status, 'retweeted_status'):
            return True
        else:
            tweet_id = status.id_str
            user_id = status.user.id_str
            created_at = status.created_at
            try:
                raw_tweet = status.extended_tweet["full_text"]
            except:
                raw_tweet = status.text

        payload = {
            'text': raw_tweet,
            'created_at': str(created_at),
            'tweet_id': tweet_id,
            'user_id': user_id
        }
        
        clean_clf = clean_proc_clf(raw_tweet)
        clean_pos = clean_proc_pos(raw_tweet)

        payload['clean_clf'] = clean_clf
        payload['clean_pos'] = clean_pos
        dumps = json.dumps(payload)
        db.lpush(STREAM_LIST_KEY, dumps)

        logger.info(payload)

        return True

    def on_error(self, status_code):
        if status_code == 420:
            logger.warning('rate limit')
            return False


def back_off(pending):
    if pending > 500:
        pending = 1
    logger.warning('Back off {} seconds'.format(pending))
    time.sleep(pending)
    pending *= 2
    return pending


if __name__ == '__main__':
    log_dir = os.path.join("storage", "streamer.log")
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_dir)

    formatter = logging.Formatter('%(asctime)s - STREAMER - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    logger.info("Start")
    
    pending = 1
    max_pending = 500
    while True:
        try:
            l = CustomListener()
            auth = OAuthHandler(APP_KEY, APP_SECRET)
            auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

            stream = Stream(auth, l)
            stream.filter(follow=TARGET_USER_ID)
        except KeyboardInterrupt:
            break
        except Exception:
            logger.error("Exception occur", exc_info=True)
            pending = back_off(pending)
        else:
            pending = back_off(pending)
