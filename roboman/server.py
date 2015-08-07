import requests

__author__ = 'grigory51'
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornkts.handlers import DefaultHandler

from webhook import WebHookHandler
from settings import options


class RobomanServer(Application):
    def __init__(self, bots=None):
        handlers = [
            (r"/telegram.(\w+)", WebHookHandler),
        ]

        if isinstance(bots, list):
            for bot in bots:
                handlers += (r"/{0}.(\w+)".format(bot.name), bot),
        else:
            bots = []

        settings = {
            'compress_response': False,
            'default_handler_class': DefaultHandler,
            'debug': options.debug,
            'bots': bots
        }

        super(RobomanServer, self).__init__(handlers, **settings)

    def start(self):
        bots = self.settings.get('bots', [])
        for bot in bots:
            r = requests.post(bot.get_method_url('setWebhook'), {'url': bot.get_webhook_url()})
            print r.text

        self.listen(options.port, options.host)
        IOLoop.instance().start()
