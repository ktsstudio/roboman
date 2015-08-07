import traceback
from tornkts import utils

__author__ = 'grigory51'
from tornkts.handlers import BaseHandler
from settings import options
import random
import string


class BaseBot(BaseHandler):
    name = None
    key = None
    access_key = None

    def __init__(self, application, request, **kwargs):
        super(BaseBot, self).__init__(application, request, **kwargs)

    @classmethod
    def _on_hook(cls, body):
        data = utils.json_loads(body)
        payload = {
            'text': data.get('message', {}).get('text', None),
            'date': data.get('message', {}).get('date', None),
            'chat_id': data.get('message', {}).get('chat', {}).get('id', None),
            'chat_title': data.get('message', {}).get('chat', {}).get('title', None),
            'from_id': data.get('message', {}).get('from', {}).get('id', None),
            'from_name': data.get('message', {}).get('from', {}).get('username', None)
        }
        try:
            cls.on_hook(payload)
        except:
            traceback.print_exc()
            pass

    @classmethod
    def get_method_url(cls, method):
        return 'https://api.telegram.org/bot' + cls.key + '/' + method

    @classmethod
    def get_webhook_url(cls):
        cls.access_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(30)])
        return options.server_name + '/telegram.' + cls.access_key
