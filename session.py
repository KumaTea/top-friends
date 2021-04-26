import json
import logging

import tweepy

from tools import query_token

twitter_token = json.loads(query_token('twitter'))
token_auth = tweepy.OAuthHandler(twitter_token['consumer_key'], twitter_token['consumer_secret'])
token_auth.set_access_token(twitter_token['access_token'], twitter_token['access_token_secret'])
twi = tweepy.API(token_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
host_user = twi.me()
twi._me = host_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
