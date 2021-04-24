import tweepy
from config import max_days
from datetime import datetime

from session import twi, logger

from tweepy.error import RateLimitError


def cursor_wrapper(tweet_list, method, host_user=twi.me().id, now=datetime.now(), max_size=None, api=twi):
    # if not host_user:
    #     host_user = api.me().id
    if 'fav' in method.lower():
        api_method = api.favorites
    else:
        api_method = api.user_timeline

    try:
        for tweet in tweepy.Cursor(api_method, id=host_user).items():
            if (now - tweet.created_at).days > max_days:
                break
            # sys.stdout.write('\r' + f'Get: {tweet.id}: {remove_new_line(tweet.text)[:70]}')
            # logger.info('.', end='')
            tweet_list.append(tweet)
            if max_size:
                if len(tweet_list) >= max_size:
                    break
    except RateLimitError:
        logger.error('RateLimitError.')

    return tweet_list
