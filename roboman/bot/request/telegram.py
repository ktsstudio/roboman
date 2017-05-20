from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.httputil import url_concat
from tornkts.utils import json_loads, encode_multipart_formdata

client = AsyncHTTPClient()


def get_method_url(method, token, url=None, params=None):
    url = url or 'https://api.telegram.org'
    url = url + '/bot' + token + '/' + method
    if params is not None:
        url = url_concat(url, params)
    return url


async def send(msg, text, credentials, url=None):
    params = {
        'text': text,
        'chat_id': msg.from_id,
    }

    req = HTTPRequest(
        get_method_url('sendMessage', credentials.get('access_token'), url=url),
        method="POST",
        body=urlencode(params)
    )

    res = await client.fetch(req)
    return json_loads(res.body)


async def send_image(msg, path, credentials, url=None):
    with open(path, 'rb') as f:
        file = ['photo', path, f.read()]
        params = {
            'chat_id': msg.from_id,
        }

        content_type, body = encode_multipart_formdata(params, [file])

        req = HTTPRequest(
            get_method_url('sendPhoto', credentials.get('access_token'), url=url),
            method="POST",
            body=body,
            headers={'Content-Type': content_type}
        )

        res = await client.fetch(req)
        return json_loads(res.body)
