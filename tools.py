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
