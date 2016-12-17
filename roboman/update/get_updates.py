import requests
import logging
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPError
from tornado import gen

try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'

logger = logging.getLogger('bot')


def get_updates(bot):
    client = AsyncHTTPClient()
    requests.post(bot.get_method_url('setWebhook'))
    logger.info('Webhook was reset')
    update_id = [None]

    async def wrapper():
        data = {}
        if update_id[0] is not None:
            data['offset'] = update_id[0]

        req = HTTPRequest(bot.get_method_url('getUpdates', data), connect_timeout=2, request_timeout=2, )
        try:
            res = await client.fetch(req)
        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 599:
                logger.warning('HTTPError: timeout %s %s' % (bot.bot_name, e.message))
            else:
                logger.exception(e)

            return False

        data = json.loads(res.body)
        if data.get('ok'):
            flag = False
            for item in data.get('result', []):
                flag = True
                if update_id[0] is None or item.get('update_id') + 1 > update_id[0]:
                    update_id[0] = item.get('update_id') + 1
                    await bot().on_hook(item)
            if flag:
                logger.info('Processing updates for %s' % (bot.bot_name,))

    return wrapper
