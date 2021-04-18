def format_text(text, length=12):
    text_l = len(text)
    if text_l == length:
        return text
    elif text_l < length:
        return text + (length-text_l)*' '
    elif text_l > 12:
        return text[:length-3] + '...'


def format_html_start(text, user, current_time):
    text = text.replace('host_user_screen_name', user.name)
    text = text.replace('top_friends_generated_date', current_time.strftime('%Y-%m-%d'))
    return text


def remove_new_line(text):
    return text.replace('\n', ' ')
