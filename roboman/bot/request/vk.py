from urllib.parse import urlencode
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat


def get_method_url(method, token, url=None, params=None):
    url = url or 'https://api.vk.com'
    url = '{url}/method/{method}?access_token={token}'.format(
        url=url,
        method=method,
        token=token
    )

    if params is not None:
        url = url_concat(url, params)
    return url


def send(msg, text, credentials, url=None):
    params = {
        'message': text,
        'user_id': msg.from_id,
    }

    return HTTPRequest(
        get_method_url('messages.send', credentials.get('access_token'), url=url),
        method="POST",
        body=urlencode(params)
    )
