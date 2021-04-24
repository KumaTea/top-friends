from config import *
from datetime import datetime
from session import twi, logger
from tweet_fetch import cursor_wrapper


def get_empty_friends_dict(user, api=twi):
    # user is an api
    friend_ids = api.friends_ids(user.id)
    logger.info(f'@{user.screen_name}\'s friends count:', len(friend_ids))
    friends = {}
    for i in friend_ids:
        friends[i] = 0
    return friends


def process_timeline(user, friends, now=datetime.now()):
    # user is an id
    timeline = []
    max_size = friends_max_query
    if user == twi._me.id or user == twi._me.screen_name:
        max_size = None
    timeline = cursor_wrapper(timeline, 'user_timeline', user, now, max_size)
    logger.info(f'@{user}\'s timeline:', len(timeline))

    for tweet in timeline:
        if tweet.user.id == user:
            if tweet.in_reply_to_user_id and tweet.in_reply_to_user_id in friends:  # reply
                reply_id = tweet.in_reply_to_user_id
                friends[reply_id] += reply_power*(max_days - (now - tweet.created_at).days)
            try:
                if tweet.is_quote_status and tweet.quoted_status.user.id in friends:  # quote retweet
                    quote_id = tweet.quoted_status.user.id
                    friends[quote_id] += quote_power*(max_days - (now - tweet.created_at).days)
            except AttributeError:  # deleted tweets
                pass
        else:  # retweets
            if tweet.user.id in friends:
                retweet_id = tweet.user.id
                friends[retweet_id] += retweet_power * (max_days - (now - tweet.created_at).days)
    return friends


def process_like(user, friends, now=datetime.now()):
    # user is an id
    likes = []
    max_size = friends_max_query
    if user == twi._me.id or user == twi._me.screen_name:
        max_size = None
    likes = cursor_wrapper(likes, 'favorites', user, now, max_size)
    logger.info(f'@{user}\'s likes:', len(likes))

    for tweet in likes:
        if tweet.user.id in friends:
            like_id = tweet.user.id
            friends[like_id] += like_power*(max_days - (now - tweet.created_at).days)
    return friends
