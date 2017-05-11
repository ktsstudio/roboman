import weakref
from roboman.bot import request
from roboman.bot.message import Message
from tornado.httpclient import HTTPError, AsyncHTTPClient
from tornkts.utils import json_loads
import logging

client = AsyncHTTPClient()
logger = logging.getLogger('bot')


class BaseBot(object):
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.store = kwargs.get('store')
        self.extra = kwargs.get('extra')
        self.settings = kwargs.get('settings', {})
        self._parent = kwargs.get('parent')

    @property
    def parent(self):
        if isinstance(self._parent, weakref.ref):
            return self._parent()
        else:
            return self._parent

    @property
    def text(self):
        return self.msg.text

    @property
    def is_telegram(self):
        return self.msg.source == Message.SOURCE_TELEGRAM

    @property
    def is_vk(self):
        return self.msg.source == Message.SOURCE_VK

    async def before_hook(self):
        pass

    async def hook(self):
        raise NotImplemented

    async def after_hook(self):
        pass

    async def run(self, cls=None, extra=None):
        success = False

        if cls is None:
            instance = self
        else:
            instance = cls(
                self.msg,
                store=self.store,
                extra=extra,
                parent=weakref.ref(self)
            )

        await instance.before_hook()

        try:
            await instance.hook()
            success = True
        except Exception as e:
            await instance.after_hook()
            raise e
        if success:
            await instance.after_hook()

    async def send(self, text):
        req = request.send(self, text)

        try:
            res = await client.fetch(req)
            return json_loads(res.body)
        except HTTPError as e:
            logger.exception(e)

    def match_command(self, commands=None, text=None):
        if commands is None:
            return False

        if text is None:
            text = self.msg.text

        if not isinstance(commands, list):
            commands = [commands]

        for command in commands:
            text = text.strip()

            if not command:
                continue

            if text.startswith(command) or text.startswith('/' + command):
                text = text[len(command):].strip()
                return {
                    'command': command,
                    'result': True,
                    'args': [i for i in text.split(' ')]
                }

        return False
