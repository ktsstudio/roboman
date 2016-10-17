import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from multiprocessing.pool import Pool

from tornado.concurrent import run_on_executor
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from tornado import gen
from tornado.ioloop import IOLoop

try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'

logger = logging.getLogger('bot')


def get_updates(bot, timeout=1000):
    client = CurlAsyncHTTPClient()
    sync_client = HTTPClient()
    pool = ThreadPoolExecutor(4)

    logger.info('Start webhook reset: {0}'.format(bot.__name__))

    req = HTTPRequest(
        bot.get_method_url('setWebhook'),
        method='GET',
    )
    sync_client.fetch(req)

    logger.info('Webhook reseted for {0}'.format(bot.__name__))
    update_id = [None]

    @gen.coroutine
    def wrapper():
        while True:
            start = datetime.now()

            data = {}
            if update_id[0] is not None:
                data['offset'] = update_id[0]

            request = HTTPRequest(
                bot.get_method_url('getUpdates', data),
                connect_timeout=2,
                request_timeout=2
            )

            try:
                res = yield client.fetch(request)
                data = json.loads(res.body)
                if data.get('ok'):
                    result = data.get('result')
                    if isinstance(result, list) and len(result) > 0:
                        for item in result:
                            if update_id[0] is None or item.get('update_id') + 1 > update_id[0]:
                                update_id[0] = item.get('update_id') + 1
                                yield pool.submit(lambda b, i: b().on_hook(i), bot, item)
                        logger.info('Processing updates for {0}'.format(bot.__name__))
            except HTTPError as e:
                if e.code == 599:
                    logger.error('Timeout getUpdates of {0}'.format(bot.__name__))
                else:
                    logger.error(e.response.body)

            end = datetime.now()
            delta = end - start

            delta = timeout - delta.total_seconds() * 1000
            if delta > 0:
                yield gen.sleep(delta / 1000.0)

    return wrapper
