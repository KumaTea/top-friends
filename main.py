from config import *
from format import *
from datetime import datetime
from session import twi, logger
from tweet_fetch import cursor_wrapper


if __name__ == '__main__':
    """
    host_user_screen_name = input('Please input your username: ') or None
    if host_user_screen_name:
        try:
            host_user = twi.get_user(host_user_screen_name)
            logger.info('User OK.')
        except TweepError:
            host_user = None
            exit('Invalid user.')
    else:
        host_user = twi.me()
    """
    logger.warning('Initializing...')
    host_user = twi.me()

    # Temporarily remove web page
    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write('Generating...')
    with open('more-info.html', 'w', encoding='utf-8') as html_file:
        html_file.write('Generating...')

    logger.warning('Getting friends list...')
    friend_ids = twi.friends_ids(host_user.id)
    logger.info('Friends count:', len(friend_ids))
    friends = {}
    for i in friend_ids:
        friends[i] = 0

    now = datetime.now()  # datetime.now(timezone(timedelta(hours=8)))

    logger.warning('Getting user timeline...')
    timeline = []
    timeline = cursor_wrapper(twi, timeline, now, 'user_timeline', host_user)
    logger.info('Timeline:', len(timeline))

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

    logger.warning('Getting user likes...')
    likes = []
    likes = cursor_wrapper(twi, likes, now, 'favorites', host_user)
    logger.info('Likes:', len(likes))

    for tweet in likes:
        if tweet.user.id in friends:
            like_id = tweet.user.id
            friends[like_id] += like_power*(max_days - (now - tweet.created_at).days)

    total_score = 0
    for i in friends:
        total_score += friends[i]
    logger.info('Total score:', total_score)

    friends = {k: v for k, v in sorted(
        friends.items(), key=lambda item: item[1], reverse=True)}

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
                           '    </tr>\n'
        more_info += friend_more_info
        logger.info(f'@{format_text(friend_info.screen_name)}\t{friend_rate}\t{friend_info.name}')
        index += 1
        if index > max_friends:
            break
    html_code += '</div>\n' \
                 '<br>\n' \
                 '<div class="footer">\n' \
                 '  <div>\n' \
                 '    <a href="more-info.html">\n' \
                 '      More Info\n' \
                 '    </a>\n' \
                 '  </div>\n' + html_end
    more_info += '  </table>\n' \
                 '</div>\n' \
                 '<br>\n' \
                 '<div class="footer">\n' \
                 '  <div>\n' \
                 '    <a href="index.html">\n' \
                 '      Back\n' \
                 '    </a>\n' \
                 '  </div>\n' + html_end
    with open('index.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html_code)
    with open('more-info.html', 'w', encoding='utf-8') as html_file:
        html_file.write(more_info)
