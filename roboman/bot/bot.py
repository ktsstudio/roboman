from asyncio import iscoroutinefunction
from urllib.parse import urlencode

from roboman.bot import request
from tornado import gen
from tornado.httpclient import HTTPRequest, HTTPError, AsyncHTTPClient
from tornado.httputil import url_concat
from roboman.telegram.inline.result import InlineQueryResult
from roboman.storages import StoreSet
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

    @property
    def text(self):
        return self.msg.text

    async def hook(self):
        raise NotImplemented

    async def send(self, text):
        req = request.send(self.msg, text)

        try:
            res = await client.fetch(req)
            return json_loads(res.body)
        except HTTPError as e:
            logger.exception(e)
