from urllib.parse import urlencode
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.httputil import url_concat
from tornkts.utils import json_loads, encode_multipart_formdata, json_dumps

client = AsyncHTTPClient()


def get_method_url(method, token=None, url=None, params=None):
    url = url or 'https://api.vk.com'
    url = '{url}/method/{method}'.format(url=url, method=method)

    if params is None:
        params = dict()

    if token:
        params.update({
            'access_token': token,
            'v': '5.64'
        })

    url = url_concat(url, params)
    return url


async def send(msg, credentials, text=None, url=None, params=None):
    if params is None:
        params = dict()

    params.update({
        'user_id': msg.from_id,
        'v': '5.64',
    })

    if text:
        params['message'] = text

    req = HTTPRequest(
        get_method_url('messages.send', credentials.get('access_token'), url=url),
        method="POST",
        body=urlencode(params)
    )

    res = await client.fetch(req)
    return json_loads(res.body)


async def send_image(msg, path, credentials, url=None):
    with open(path, 'rb') as f:
        file = ['photo', path, f.read()]
        fields = {
            'v': '5.64',
            'access_token': credentials.get('access_token')
        }
        content_type, body = encode_multipart_formdata(fields, [file])

        try:
            req = HTTPRequest(
                url=get_method_url('photos.getMessagesUploadServer', credentials.get('access_token'), url=url),
            )

            res = await client.fetch(req)
            res = json_loads(res.body)

            upload_url = res['response']['upload_url']
        except Exception as e:
            raise Exception('Exception photos.getMessagesUploadServer: ' + str(e))

        try:
            req = HTTPRequest(
                url=upload_url,
                method="POST",
                body=body,
                headers={'Content-Type': content_type}
            )
            res = await client.fetch(req)
            res = json_loads(res.body)
        except Exception as e:
            raise Exception('Exception upload: ' + str(e))

        try:
            req = HTTPRequest(
                url=get_method_url(
                    'photos.saveMessagesPhoto', credentials.get('access_token'),
                    url=url,
                    params={
                        'server': res['server'],
                        'photo': res['photo'],
                        'hash': res['hash'],
                        'v': '5.64',
                    }
                ),

            )

            res = await client.fetch(req)
            res = json_loads(res.body)

            owner_id = res['response'][0]['owner_id']
            media_id = res['response'][0]['id']
        except Exception as e:
            raise Exception('Exception photos.saveMessagesPhoto: ' + str(e))

        return await send(msg, credentials, url=url, params={
            'attachment': 'photo%s_%s' % (owner_id, media_id),
        })
