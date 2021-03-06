from datetime import datetime

import tweepy
from tweepy.error import RateLimitError

from config import max_days
from session import twi, logger


def cursor_wrapper(tweet_list, method, host_user=twi.me().id, now=datetime.now(), max_size=None, api=twi):
    # if not host_user:
    #     host_user = api.me().id
    if 'fav' in method.lower():
        api_method = api.favorites
        cursor = tweepy.Cursor(api_method, id=host_user,
                               trim_user=False,  # needed to count retweets
                               exclude_replies=False,
                               include_rts=True)
    else:
        api_method = api.user_timeline
        cursor = tweepy.Cursor(api_method, id=host_user)

    try:
        for tweet in cursor.items():
            if (now - tweet.created_at).days > max_days:
                break
            # sys.stdout.write('\r' + f'Get: {tweet.id}: {remove_new_line(tweet.text)[:70]}')
            tweet_list.append(tweet)
            if max_size:
                if len(tweet_list) >= max_size:
                    break
    except RateLimitError:
        logger.error('RateLimitError.')

    return tweet_list
