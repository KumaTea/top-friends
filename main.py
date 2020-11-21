import sys
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


def format_html_start(text, user, current_time):
    text = text.replace('host_user_screen_name', user.name)
    text = text.replace('top_friends_generated_date', current_time.strftime('%Y-%m-%d'))
    return text


max_days = 30
max_friends = 30
like_power = 1
reply_power = 3*like_power
retweet_power = 5*like_power
quote_power = 5*like_power


print('Initializing...')
twitter_token = json.loads(query_token('twitter'))
token_auth = tweepy.OAuthHandler(twitter_token['consumer_key'], twitter_token['consumer_secret'])
token_auth.set_access_token(twitter_token['access_token'], twitter_token['access_token_secret'])
twi = tweepy.API(token_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
# twi = tweepy.API(token_auth)


if __name__ == '__main__':
    host_user_screen_name = input('Please input your username: ')
    try:
        host_user = twi.get_user(host_user_screen_name)
        print('User OK.')
    except TweepError:
        host_user = None
        exit('Invalid user.')

    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write('Generating...')
    with open('more-info.html', 'w', encoding='utf-8') as html_file:
        html_file.write('Generating...')

    print('Getting friends list...')
    friend_ids = twi.friends_ids()
    print('Friends count:', len(friend_ids))
    friends = {}
    for i in friend_ids:
        friends[i] = 0

    now = datetime.now()

    rmnl = lambda t: t.replace('\n', ' ')

    print('Getting user timeline...')
    timeline = []
    try:
        for tweet in tweepy.Cursor(twi.user_timeline, id=host_user_screen_name).items():
            if (now - tweet.created_at).days > max_days:
                break
            sys.stdout.write('\r' + f'Get: {tweet.id}: {rmnl(tweet.text)[:70]}')
            timeline.append(tweet)
    except RateLimitError:
        print('RateLimitError.')
    print('Timeline:', len(timeline))
    for tweet in timeline:
        if tweet.user.id == host_user.id:
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

    print('Getting user likes...')
    likes = []
    try:
        for tweet in tweepy.Cursor(twi.favorites, id=host_user_screen_name).items():
            if (now - tweet.created_at).days > max_days:
                break
            sys.stdout.write('\r' + f'Get: {tweet.id}: {rmnl(tweet.text)[:70]}')
            likes.append(tweet)
    except RateLimitError:
        print('RateLimitError.')
    print('Likes:', len(likes))
    for tweet in likes:
        if tweet.user.id in friends:
            like_id = tweet.user.id
            friends[like_id] += like_power*(max_days - (now - tweet.created_at).days)

    total_score = 0
    for i in friends:
        total_score += friends[i]
    print('Total score:', total_score)

    friends = {k: v for k, v in sorted(friends.items(), key=lambda item: item[1], reverse=True)}

    first_friend_id = list(friends.keys())[0]
    first_friend = twi.get_user(first_friend_id)
    max_rate = round(100*friends[first_friend_id]/total_score)

    with open('html_start.txt', 'r', encoding='utf-8') as f:
        html_start = format_html_start(f.read(), host_user, now)
    with open('html_end.txt', 'r', encoding='utf-8') as f:
        html_end = f.read()

    html_code = ''
    more_info = ''
    html_code += html_start + '<div class="container">\n'
    more_info += html_start + '<div>\n' \
                              '  <table style="width:85%">\n' \
                              '    <tr>\n' \
                              '      <th>Username</th>\n' \
                              '      <th>Percentage</th>\n' \
                              '      <th>Name</th>\n' \
                              '    </tr>'
    index = 0
    for i in friends:
        friend_info = twi.get_user(i)
        profile_url = friend_info.profile_image_url_https.replace('_normal', '')
        friend_rate = format(100*friends[i]/total_score, '.2f') + '%'
        friend_html = f'  <a href="https://twitter.com/{friend_info.screen_name}"><img ' \
                      f'class="avatar" src="{profile_url}" ' \
                      f'alt="Avatar" style="width:{round(240*friends[i]/friends[first_friend_id])}px"/></a>\n'
                      #f'<div class="info"><span style="color: black">{friend_info.name}</span><br><span style="color: black">{friend_info.screen_name}</span><br><progress max="{round(friends[first_friend_id])}" value="{round(friends[i]/friends[first_friend_id])}"></progress>&nbsp;&nbsp;<span>{friend_rate}</span></div>'
        html_code += friend_html
        friend_more_info = '    <tr>\n' \
                           f'      <th>@{friend_info.screen_name}</th>\n' \
                           f'      <th>{friend_rate}</th>\n' \
                           f'      <th>{friend_info.name}</th>\n' \
                           '    </tr>'
        more_info += friend_more_info
        print(f'@{format_text(friend_info.screen_name)}\t{friend_rate}\t{friend_info.name}')
        index += 1
        if index > max_friends:
            break
    html_code += '</div>\n' \
                 '<br>\n' \
                 '<div style="text-align: center">\n' \
                 '  <a href="more-info.html">\n' \
                 '    More Info\n' \
                 '  </a>\n' + html_end
    more_info += '  </table>\n' \
                 '</div>\n' \
                 '<br>\n' \
                 '<div style="text-align: center">\n' \
                 '  <a href="index.html">\n' \
                 '    Back\n' \
                 '  </a>\n' + html_end
    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html_code)
    with open('more-info.html', 'w', encoding='utf-8') as html_file:
        html_file.write(more_info)
