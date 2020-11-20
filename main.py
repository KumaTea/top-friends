import json
import base64
import tweepy
from datetime import datetime
from tweepy.error import TweepError, RateLimitError


def read_file(filename, encrypt=False):
    if encrypt:
        with open(filename, 'rb') as f:
            return base64.b64decode(f.read()).decode('utf-8')
    else:
        with open(filename, 'r') as f:
            return f.read()


def query_token(token_id):
    return read_file(f'token_{token_id}', True)


def format_text(text, length=12):
    l = len(text)
    if l == length:
        return text
    elif l < length:
        return text + (length-l)*' '
    elif l > 12:
        return text[:length-3] + '...'


max_days = 30
max_friends = 30
like_power = 1
reply_power = 3*like_power


twitter_token = json.loads(query_token('twitter'))
token_auth = tweepy.OAuthHandler(twitter_token['consumer_key'], twitter_token['consumer_secret'])
token_auth.set_access_token(twitter_token['access_token'], twitter_token['access_token_secret'])
# twi = tweepy.API(token_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
twi = tweepy.API(token_auth)


host_user = input('Please input your username: ')
try:
    twi.get_user(host_user)
    print('User OK.')
except TweepError:
    exit('Invalid user.')


friend_ids = twi.friends_ids()
print('Friends count:', len(friend_ids))
friends = {}
for i in friend_ids:
    friends[i] = 0


now = datetime.now()


timeline = []
try:
    for tweet in tweepy.Cursor(twi.user_timeline, id=host_user).items():
        if (now - tweet.created_at).days > max_days:
            break
        timeline.append(tweet)
except RateLimitError:
    print('RateLimitError.')
print('Timeline:', len(timeline))
for tweet in timeline:
    if (reply_id := tweet.in_reply_to_user_id) and reply_id in friends:
        friends[reply_id] += reply_power*(max_days - (now - tweet.created_at).days)

likes = []
try:
    for tweet in tweepy.Cursor(twi.favorites, id=host_user).items():
        if (now - tweet.created_at).days > max_days:
            break
        likes.append(tweet)
except RateLimitError:
    print('RateLimitError.')
print('Likes:', len(likes))
for tweet in likes:
    if (like_id := tweet.user.id) in friends:
        friends[like_id] += like_power*(max_days - (now - tweet.created_at).days)


total_score = 0
for i in friends:
    total_score += friends[i]
print('Total score:', total_score)

friends = {k: v for k, v in sorted(friends.items(), key=lambda item: item[1], reverse=True)}

first_friend_id = list(friends.keys())[0]
first_friend = twi.get_user(first_friend_id)
max_rate = round(100*friends[first_friend_id]/total_score)

html_start = f'<!DOCTYPE html><html><head> <meta charset="utf-8"> <title>Top Friends by @{host_user}</title> <meta ' \
             'name="viewport" content="width=device-width, initial-scale=1.0"> <style>img.avatar{border-radius: 50%; ' \
             '}.container{position: relative; text-align: center; color: white; /*transform: rotate(' \
             '90deg)*/}.info{position: absolute; top: 50%; left: 50%; transform: translate(-50%, ' \
             '-50%);}</style></head><body><div class="container">'
# opacity: 0.5;
html_end = '</div></body></html>'


html = ''
html += html_start
index = 0
for i in friends:
    friend_info = twi.get_user(i)
    profile_url = friend_info.profile_image_url_https.replace('_normal', '')
    friend_rate = format(100*friends[i]/total_score, '.2f') + '%'
    friend_html = f'<img class="avatar" src="{profile_url}" ' \
                  f'alt="Avatar" style="width:{round(240*friends[i]/friends[first_friend_id])}px"/>'
                  #f'<div class="info"><span style="color: black">{friend_info.name}</span><br><span style="color: black">{friend_info.screen_name}</span><br><progress max="{round(friends[first_friend_id])}" value="{round(friends[i]/friends[first_friend_id])}"></progress>&nbsp;&nbsp;<span>{friend_rate}</span></div>'
    html += friend_html
    print(f'@{format_text(friend_info.screen_name)}\t{friend_rate}\t{friend_info.name}')
    index += 1
    if index > max_friends:
        break
html += html_end

with open('index.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html)
