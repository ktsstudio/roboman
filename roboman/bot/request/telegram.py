from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat


def get_method_url(method, token, params=None):
    url = 'https://api.telegram.org/bot' + token + '/' + method
    if params is not None:
        url = url_concat(url, params)
    return url


def send(msg, text):
    params = {
        'text': text,
        'chat_id': msg.from_id,
    }

    return HTTPRequest(
        get_method_url('sendMessage', msg.credentials.get('access_token')),
        method="POST",
        body=urlencode(params)
    )
