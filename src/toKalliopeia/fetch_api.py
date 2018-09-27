import json
import requests


def _send(endpoint, type, data=None, token=None):
    # uri = 'http://api.kalliopeia.killedbynlp.com/' + endpoint
    uri = "https://api.kalliopeia.ijcai-20.org/" + endpoint
    # uri = "http://localhost:8081/" + endpoint
    data = json.dumps(data)
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = "Bearer " + token
    if type.lower() == 'get':
        return requests.get(uri, headers=headers).json()
    elif type.lower() == 'post':
        return requests.post(uri, data, headers=headers).json()
    else:
        raise ValueError("type '" + token + "' is not defined.")


def get_access_token(name, password):
    request_data = {
        'name': name,
        'password': password
    }
    response = _send(endpoint='login', data=request_data, type='post')
    return response['token']


def load_thread(token, thread_i):
    en_p = "threads/" + str(thread_i)
    return _send(endpoint=en_p, token=token, type="get")


def load_threads(token):
    return _send(endpoint="threads", type="get", token=token)


def load_users(token):
    return _send(endpoint="users", type="get", token=token)


def load_user(token, ui):
    en_p = "users/" + str(ui)
    return _send(endpoint=en_p, token=token, type="get")


def create_post(token, data):
    _send(endpoint="posts", token=token, data=data, type="post")


def create_user(token, data):
    _send(endpoint="signup", token=token, data=data, type="post")

