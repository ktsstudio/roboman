from urllib.parse import urlencode
from roboman.broker.handlers import WorkerHandler, HookHandler
from roboman.broker.msg_queue import buckets
from roboman.log import get_logger
from tornado import gen
from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornkts.base.server_response import ServerError

logger = get_logger('broker')


class Broker(Application):
    def __init__(self, *args, **kwargs):
        handlers = [
            (r"/([0-9a-zA-Z]+)/hook.(.*)", HookHandler),
            (r"/([0-9a-zA-Z]+)/worker.(.*)", WorkerHandler),
        ]

        if kwargs.get('handlers'):
            handlers += kwargs.get('handlers')

        settings = {
            'compress_response': False,
            'debug': False,
        }

        if kwargs.get('settings'):
            settings.update(kwargs.get('settings'))

        super().__init__(handlers, **settings)

    def get_messenger_settings(self, name):
        settings = self.settings.get('messengers', {}).get(name)
        if not isinstance(settings, dict):
            raise ServerError(ServerError.INTERNAL_SERVER_ERROR, description='%s_not_settings' % name)

        return settings

    def set_telegram_webhook(self):
        result = False
        telegram = self.get_messenger_settings('telegram')
        http_client = HTTPClient()

        if 'bots' in telegram:
            for bucket, bot in telegram['bots'].items():
                try:
                    logger.info('Installing telegram webhook: %s' % bot['hook_url'])

                    request = HTTPRequest(
                        'https://api.telegram.org/bot{0}/setWebhook'.format(bot['access_token']),
                        method="POST",
                        body=urlencode({'url': bot['hook_url']})
                    )
                    http_client.fetch(request)

                    logger.info('Telegram webhook %s successfully install' % bot['hook_url'])
                    result = True
                except Exception as e:
                    logger.error('Fail set telegram webhook: {0}'.format(str(e)))

        http_client.close()
        return result


@gen.coroutine
def stats():
    while True:
        yield gen.sleep(3)

        for key, queue in buckets.items():
            queue_stats = queue.stats()

            print('Stats {key}: new: {new}, work: {work}, total:{total}\nLocks: {locks}'.format(
                new=queue_stats.get('new'),
                work=queue_stats.get('work'),
                total=queue_stats.get('total'),
                locks=', '.join(list(map(str, list(queue.locks)))),
                key=key
            ))


if __name__ == '__main__':
    loop = IOLoop.instance()

    broker = Broker()
    broker.listen(5555)

    loop.add_callback(stats)
    loop.start()
