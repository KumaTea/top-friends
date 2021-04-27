import base64


def read_file(filename, encrypt=False):
    if encrypt:
        with open(filename, 'rb') as f:
            return base64.b64decode(f.read()).decode('utf-8')
    else:
        with open(filename, 'r') as f:
            return f.read()


def query_token(token_id):
    return read_file(f'token_{token_id}', True)


def sort_dict_by_value(dictionary, reverse=True):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse)}


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
