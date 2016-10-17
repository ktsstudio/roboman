from tornado.httpclient import HTTPClient, HTTPRequest
from urllib.parse import urlencode
from roboman.bot import BaseBot
from roboman.update.get_updates import get_updates
from roboman.update.webhook import WebHookHandler
from tornkts.base.server_response import ServerError
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornkts.handlers import DefaultHandler
from tornado.ioloop import PeriodicCallback
import logging

__author__ = 'grigory51'

logger = logging.getLogger('roboman')


class RobomanServer(Application):
    def __init__(self, **kwargs):
        bots = kwargs.get('bots')
        mode = kwargs.get('mode', BaseBot.MODE_GET_UPDATES)

        handlers = []

        if mode == BaseBot.MODE_HOOK:
            handlers += [
                (r"/telegram.(\w+)", WebHookHandler),
            ]

        if not isinstance(bots, list):
            bots = []

        settings = {
            'compress_response': False,
            'default_handler_class': DefaultHandler,
            'bots': bots,
            'mode': mode
        }

        handlers += kwargs.get('handlers', [])
        settings.update(kwargs.get('settings', {}))
        super(RobomanServer, self).__init__(handlers, **settings)

    def start(self, loop_start=True):
        host = self.settings.get('host', '127.0.0.1')
        port = self.settings.get('port', 8000)

        bots = self.settings.get('bots', [])
        mode = self.settings.get('mode', BaseBot.MODE_HOOK)
        update_interval = self.settings.get('update_interval', 1000)

        sync_client = HTTPClient()
        io_loop = IOLoop.instance()

        for bot in bots:
            if mode == BaseBot.MODE_HOOK:
                req = HTTPRequest(
                    bot.get_method_url('setWebhook'),
                    method='POST',
                    body=urlencode({'url': bot.get_webhook_url()})
                )
                sync_client.fetch(req)
            elif mode == BaseBot.MODE_GET_UPDATES:
                io_loop.add_callback(get_updates(bot))
            else:
                raise ServerError(ServerError.INTERNAL_SERVER_ERROR, description='Bad server mode')

        logger.info('Start Roboman')
        logger.info('Bots: %s' % (', '.join([bot.__name__ for bot in bots])))

        self.listen(port, host)
        if loop_start:
            io_loop.start()
