from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat
from tornkts.utils import json_dumps


def get_method_url(method, token, params=None):
    url = 'https://api.vk.com/method/{method}?access_token={token}'.format(
        method=method,
        token=token
    )

    if params is not None:
        url = url_concat(url, params)
    return url


def send(msg, text):
    params = {
        'message': text,
        'user_id': msg.from_id,
    }

    return HTTPRequest(
        get_method_url('messages.send', msg.credentials.get('access_token')),
        method="POST",
        body=urlencode(params)
    )
