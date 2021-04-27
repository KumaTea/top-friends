from tools import *
from session import host_user
from tf_func import *

if __name__ == '__main__':
    """
    ============ C O M M E N T ============
    
    Initialization and authentication.
    
    ============ C O M M E N T ============
    """

    logger.info('Initializing...')
    now = datetime.now()  # datetime.now(timezone(timedelta(hours=8)))

    # Temporarily remove web page

    """
    ============ C O M M E N T ============

    Getting friends list.

    ============ C O M M E N T ============
    """

    logger.info('Getting friends list...')
    friends = get_empty_friends_dict(host_user.id)
    # friends_info = friends.copy()

    """
    ============ C O M M E N T ============

    Getting user timeline and like, then process them.

    ============ C O M M E N T ============
    """

    logger.info('Processing user timeline...')
    friends = process_timeline(twi._me.id, friends, now)

    logger.info('Processing user likes...')
    friends = process_like(twi._me.id, friends, now)

    """
    ============ C O M M E N T ============

    Getting friends' friends.

    ============ C O M M E N T ============
    """

    friends = sort_dict_by_value(friends)
    friends_info = {k: 0 for k in list(friends.keys())}

    if check_mutual_top:
        friends, friends_info = process_friends_info(friends, friends_info, me=twi._me.id, now=now)
    else:
        logger.warning('Skip mutual top friends check.')

    """
    ============ C O M M E N T ============

    Get initial scores.

    ============ C O M M E N T ============
    """

    total_score = 0
    for i in friends:
        total_score += friends[i]
    logger.info(f'Total score: {total_score}')

    friends = sort_dict_by_value(friends)

    """
    ============ C O M M E N T ============

    Writting HTML.

    ============ C O M M E N T ============
    """

    first_friend_id = list(friends.keys())[0]
    max_rate = round(100 * friends[first_friend_id] / total_score)

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
                              '      <th>Mutual</th>\n' \
                              '    </tr>'
    index = 0
    for i in friends:
        friend_info = twi.get_user(i)
        profile_url = friend_info.profile_image_url_https.replace('_normal', '')
        friend_rate = format(100 * friends[i] / total_score, '.2f') + '%'
        mutual_tag, is_mutual = get_mutual(i, friends_info)

        friend_html = f'  <span>' \
                      f'<a href="https://twitter.com/{friend_info.screen_name}">' \
                      f'<img class="avatar{mutual_tag}" src="{profile_url}" ' \
                      f'alt="Avatar" style="width:{round(240 * friends[i] / friends[first_friend_id])}px" />' \
                      f'</a>' \
                      f'  </span>\n'
        html_code += friend_html
        friend_more_info = '    <tr>\n' \
                           f'      <th>@{friend_info.screen_name}</th>\n' \
                           f'      <th>{friend_rate}</th>\n' \
                           f'      <th>{friend_info.name}</th>\n' \
                           f'      <th>{is_mutual}</th>\n' \
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
