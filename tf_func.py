import pickle
from datetime import datetime

from tqdm import trange

from config import *
from session import twi, logger
from tools import sort_dict_by_value
from tweet_fetch import cursor_wrapper


def get_empty_friends_dict(user, api=twi):
    # user is an int
    friend_ids = api.friends_ids(user)
    logger.info(f'{user}\'s friends count: {len(friend_ids)}')
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
    logger.info(f'{user}\'s timeline: {len(timeline)}')

    for tweet in timeline:
        if tweet.user.id == user:
            if tweet.in_reply_to_user_id and tweet.in_reply_to_user_id in friends:  # reply
                reply_id = tweet.in_reply_to_user_id
                friends[reply_id] += reply_power * (max_days - (now - tweet.created_at).days)
            try:
                if tweet.is_quote_status and tweet.quoted_status.user.id in friends:  # quote retweet
                    quote_id = tweet.quoted_status.user.id
                    friends[quote_id] += quote_power * (max_days - (now - tweet.created_at).days)
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
    logger.info(f'{user}\'s likes: {len(likes)}')

    for tweet in likes:
        if tweet.user.id in friends:
            like_id = tweet.user.id
            friends[like_id] += like_power * (max_days - (now - tweet.created_at).days)
    return friends


def get_friend_info(friend, now=datetime.now()):
    friend_friends = get_empty_friends_dict(friend)
    friend_friends = process_timeline(friend, friend_friends, now)
    friend_friends = process_like(friend, friend_friends, now)
    return sort_dict_by_value(friend_friends)


def get_friends_info(friends_info, now=datetime.now()):
    for i in trange(query_friends):
        friend = list(friends_info.keys())[i]
        logger.info(f'Getting friends info: {friend}')
        if not friends_info[friend]:
            friends_info[friend] = get_friend_info(friend, now)
        with open('friends_info.p', 'wb') as f:
            pickle.dump(friends_info, f)
    return friends_info


def get_mutual_top_power(rank):
    # Starts from 0
    if rank > mutual_top_power['range']:
        return mutual_top_power['last']
    else:
        return mutual_top_power['first'] - rank * (mutual_top_power['first'] - mutual_top_power['last']) / \
               mutual_top_power['range']


def process_friends_info(friends, friends_info, me=twi._me.id, now=datetime.now()):
    with open('friends.p', 'wb') as f:
        pickle.dump(friends, f)
    friends_info = get_friends_info(friends_info, now)
    for i in friends:
        rank = mutual_top_power['last']
        try:
            friend_index = list(friends_info[i].keys()).index(me)
            rank = get_mutual_top_power(friend_index)
            logger.info(f'You get {friend_index} in {i}.')
            print(f'You get {friend_index} in {i}.')
            friends_info[i]['index'] = friend_index
        except (AttributeError, ValueError) as e:
            logger.error('Not found!', i)
            if friends_info[i]:
                friends_info[i]['index'] = None
            else:
                friends_info[i] = {
                    'index': None
                }
        friends[i] = rank * friends[i]
        with open('friends_w.p', 'wb') as f:
            pickle.dump(friends, f)
    return friends, friends_info


def get_mutual(friend, friends_info):
    index = friends_info[friend]['index']
    mutual_tag = ''
    is_mutual = 'No'
    if index or index == 0:
        if type(index) is int:
            if index < mutual_top_power['range']:
                mutual_tag = ' ' + 'mutual'
                is_mutual = index + 1
            else:
                is_mutual = f'Ex ({index})'
    return mutual_tag, is_mutual
