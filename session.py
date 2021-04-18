import json
import tweepy
import logging
from tools import query_token


twitter_token = json.loads(query_token('twitter'))
token_auth = tweepy.OAuthHandler(twitter_token['consumer_key'], twitter_token['consumer_secret'])
token_auth.set_access_token(twitter_token['access_token'], twitter_token['access_token_secret'])
twi = tweepy.API(token_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
