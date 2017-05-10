import weakref
from asyncio import iscoroutinefunction
from urllib.parse import urlencode

from roboman.bot import request
from roboman.bot.message import Message
from tornado import gen
from tornado.httpclient import HTTPRequest, HTTPError, AsyncHTTPClient
from tornado.httputil import url_concat
from roboman.telegram.inline.result import InlineQueryResult
from roboman.telegram.keyboard import Keyboard
from tornkts import utils
from tornkts.utils import json_loads
import random
import string
import logging

client = AsyncHTTPClient()
logger = logging.getLogger('bot')


class BaseBot(object):
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.store = kwargs.get('store')
        self.extra = kwargs.get('extra')
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
        except Exception as e:
            raise e
        finally:
            await instance.after_hook()

    async def send(self, text):
        req = request.send(self.msg, text)

        try:
            res = await client.fetch(req)
            return json_loads(res.body)
        except HTTPError as e:
            logger.exception(e)
