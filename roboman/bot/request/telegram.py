from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat


def get_method_url(method, token, url=None, params=None):
    url = url or 'https://api.telegram.org'
    url = url + '/bot' + token + '/' + method
    if params is not None:
        url = url_concat(url, params)
    return url


def send(msg, text, credentials, url=None):
    params = {
        'text': text,
        'chat_id': msg.from_id,
    }

    return HTTPRequest(
        get_method_url('sendMessage', credentials.get('access_token'), url=url),
        method="POST",
        body=urlencode(params)
    )
