import tweepy
from session import logger
from config import max_days
from tweepy.error import RateLimitError


def cursor_wrapper(host, tweet_list, now, method, host_user=None):
    if not host_user:
        host_user = host.me().id
    if 'fav' in method.lower():
        api_method = host.favorites
    else:
        api_method = host.user_timeline

    try:
        for tweet in tweepy.Cursor(api_method, id=host_user.id).items():
            if (now - tweet.created_at).days > max_days:
                break
            # sys.stdout.write('\r' + f'Get: {tweet.id}: {remove_new_line(tweet.text)[:70]}')
            # logger.info('.', end='')
            tweet_list.append(tweet)
    except RateLimitError:
        logger.error('RateLimitError.')

    return tweet_list
