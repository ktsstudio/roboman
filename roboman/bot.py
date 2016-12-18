from asyncio import iscoroutinefunction, iscoroutine
from urllib.parse import urlencode
import requests
import ujson
from tornado import gen
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat
from tornkts import utils
import random
import string
import logging

from roboman.storages import StoreSet
from .keyboard import Keyboard

try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'


class BaseBot(object):
    MODE_HOOK = 'hook'
    MODE_GET_UPDATES = 'get_updates'

    bot_name = None
    bot_key = None
    access_key = None
    _raw_data = None

    connection = requests.Session()
    client = CurlAsyncHTTPClient()

    def __init__(self, parent_bot=None, chat_id=None, text=''):
        super().__init__()
        sub_bot = isinstance(parent_bot, BaseBot) if parent_bot is not None else False

        self.parent_bot = parent_bot if sub_bot else None
        self.text = text
        self.chat_id = chat_id
        self.logger = logging.getLogger(self.bot_name)

        self.store = StoreSet(self.define_stores())

        if sub_bot:
            self.__class__.bot_key = parent_bot.bot_key

    async def run_bot(self, cls, extra_data=None):
        bot = cls(parent_bot=self, chat_id=self.chat_id, text=self.text)

        data = self._raw_data
        if data is None:
            data = {}

        if 'extra' not in data:
            data['extra'] = {}

        data['extra'].update(extra_data if extra_data is not None else {})

        await bot.on_hook(data)

    def define_stores(self):
        return {}

    def _before_hook(self, payload):
        return payload

    def _on_hook(self, payload):
        raise NotImplemented

    async def refresh(self):
        await self.on_hook(self._raw_data)

    def before_hook(self, data):
        self.text = str(data.get('text', '')).strip()
        self.chat_id = data.get('chat_id', None)
        return self._before_hook(data)

    async def on_hook(self, data):
        self._raw_data = data

        message = data.get('message')
        if not isinstance(message, dict):
            message = data.get('callback_query', {}).get('message')
            if isinstance(message, dict):
                user = data.get('callback_query', {}).get('from')
            else:
                message = {}
                user = {}
        else:
            user = message.get('from', {})

        if isinstance(message, dict):
            payload = {
                'message_id': message.get('message_id'),
                'text': message.get('text'),
                'date': message.get('date'),

                'chat_id': message.get('chat', {}).get('id', None),
                'chat_title': message.get('chat', {}).get('title', None),

                'from_id': user.get('id', None),
                'from_username': user.get('username', None),
                'from_first_name': user.get('first_name', None),
                'from_last_name': user.get('last_name', None),

                'location': message.get('location', None),
                'photo': message.get('photo', None),

                'callback_query': data.get('callback_query', {}).get('data', None),
                'callback_query_id': data.get('callback_query', {}).get('id', None),
                'extra': data.get('extra', {}),

                'contact': message.get('contact')
            }

            try:
                updated_payload = self.before_hook(payload)
                if updated_payload:
                    payload = updated_payload

                if iscoroutinefunction(self._on_hook):
                    await self._on_hook(payload)
                else:
                    self._on_hook(payload)

            except Exception as e:
                if isinstance(e, HTTPError) and e.code == 599:
                    self.logger.warning('HTTPError: timeout %s' % self.bot_name)
                else:
                    self.logger.exception(e)

    def match_command(self, commands=None, text=None):
        if commands is None:
            return False

        if text is None:
            text = self.text if self.text is not None else ''

        if not isinstance(commands, list):
            commands = [commands]

        for command in commands:
            text = text.strip()
            if text.startswith(command) or text.startswith('/' + command):
                text = text[len(command):].strip()
                return {
                    'command': command,
                    'result': True,
                    'args': [i for i in text.split(' ')]
                }

        return False

    @gen.coroutine
    def send(self, text='', **params):
        if 'text' not in params:
            params['text'] = text
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id
        if 'reply_markup' in params and isinstance(params['reply_markup'], Keyboard):
            params['reply_markup'] = params['reply_markup'].to_json()

        req = HTTPRequest(
            self.get_method_url('sendMessage'),
            method="POST",
            body=urlencode(params)
        )

        try:
            res = yield self.client.fetch(req)
            data = ujson.loads(res.body)
            return data.get('result', {})
        except HTTPError as e:
            self.logger.error(e.response.body)

    @gen.coroutine
    def answer_callback_query(self, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        req = HTTPRequest(
            self.get_method_url('answerCallbackQuery'),
            method="POST",
            body=urlencode(params)
        )

        try:
            yield self.client.fetch(req)
        except HTTPError as e:
            self.logger.error(e.response.body)

    @gen.coroutine
    def send_photo(self, files, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id
        if 'reply_markup' in params and isinstance(params['reply_markup'], Keyboard):
            params['reply_markup'] = params['reply_markup'].to_json()

        kwargs = dict(method="POST")

        if isinstance(files, str):
            params['photo'] = files
            kwargs['body'] = urlencode(params)
        else:
            content_type, body = utils.encode_multipart_formdata(params, files)

            kwargs['headers'] = {'Content-Type': content_type},
            kwargs['body'] = body

        req = HTTPRequest(self.get_method_url('sendPhoto'), **kwargs)

        try:
            yield self.client.fetch(req)
        except HTTPError as e:
            self.logger.error(e.response.body)

    @gen.coroutine
    def send_location(self, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        req = HTTPRequest(
            self.get_method_url('sendLocation'),
            method="POST",
            body=urlencode(params)
        )

        res = yield self.client.fetch(req)
        if res.code != 200:
            self.logger.error(res.body)

    @gen.coroutine
    def edit_message_text(self, message_id, text='', **params):
        params['message_id'] = message_id

        if 'text' not in params:
            params['text'] = text
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id
        if 'reply_markup' in params and isinstance(params['reply_markup'], Keyboard):
            params['reply_markup'] = params['reply_markup'].to_json()

        req = HTTPRequest(
            self.get_method_url('editMessageText'),
            method="POST",
            body=urlencode(params)
        )

        try:
            res = yield self.client.fetch(req)
            data = ujson.loads(res.body)
            return data.get('result', {})
        except HTTPError as e:
            self.logger.error(e.response.body)

    def get_file_url(self, path):
        return 'https://api.telegram.org/file/bot' + self.bot_key + '/' + path

    @classmethod
    def get_method_url(cls, method, params=None):
        url = 'https://api.telegram.org/bot' + cls.bot_key + '/' + method
        if params is not None:
            url = url_concat(url, params)
        return url

    @classmethod
    def get_webhook_url(cls):
        cls.access_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(30)])
        return options.server_schema + '://' + options.server_name + '/telegram.' + cls.access_key
