import json
import requests


def _send(endpoint, type, data=None, token=None):
    uri = 'http://api.kalliopeia.killedbynlp.com/' + endpoint
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
        'password': password,
    }
    response = _send(endpoint='login', data=request_data, type='post')
    return response['token']


def load_thread(token, data, thread_i):
    en_p = "thread" + str(thread_i)
    return _send(endpoint=en_p, data=data, token=token, type="get")


def load_threads(token):
    return _send(endpoint="threads", type="get", token=token)
