import traceback
from urllib.parse import urlencode
import requests
from tornado import gen
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat
from tornkts import utils
import random
import string
import logging
from .keyboard import Keyboard

try:
    import ujson as json
except:
    import json as json

__author__ = 'grigory51'


class BaseBot(object):
    MODE_HOOK = 'hook'
    MODE_GET_UPDATES = 'get_updates'

    name = None
    key = None
    access_key = None

    connection = requests.Session()
    client = CurlAsyncHTTPClient()

    def __init__(self):
        super().__init__()
        self.text = ''
        self.chat_id = None
        self.logger = logging.getLogger(self.name)

    def _before_hook(self, payload):
        pass

    def _on_hook(self, payload):
        raise NotImplemented

    def before_hook(self, data):
        self.text = data.get('text', '')
        self.chat_id = data.get('chat_id', None)
        self._before_hook(data)

    def on_hook(self, data):
        message = data.get('message')
        if not isinstance(message, dict):
            message = data.get('callback_query', {}).get('message')
            if isinstance(message, dict):
                user = data.get('callback_query', {}).get('from')
            else:
                user = {}
        else:
            user = message.get('from', {})

        if isinstance(message, dict):
            payload = {
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
                'callback_query_id': data.get('callback_query', {}).get('id', None)
            }

            try:
                updated_payload = self.before_hook(payload)
                if updated_payload:
                    payload = updated_payload
                self._on_hook(payload)
            except:
                traceback.print_exc()

    def match_command(self, commands=None, text=None):
        if commands is None:
            return False

        if text is None:
            text = self.text

        if not isinstance(commands, list):
            commands = [commands]

        for command in commands:
            text = text.strip()
            if text.startswith(command):
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

        res = yield self.client.fetch(req)
        if res.code != 200:
            self.logger.error(res.body)

    @gen.coroutine
    def answer_callback_query(self, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id

        req = HTTPRequest(
            self.get_method_url('answerCallbackQuery'),
            method="POST",
            body=urlencode(params)
        )

        res = yield self.client.fetch(req)
        if res.code != 200:
            self.logger.error(res.body)

    @gen.coroutine
    def send_photo(self, files, **params):
        if 'chat_id' not in params:
            params['chat_id'] = self.chat_id
        if 'reply_markup' in params and isinstance(params['reply_markup'], Keyboard):
            params['reply_markup'] = params['reply_markup'].to_json()

        #        res = self.connection.post(self.get_method_url('sendPhoto'), files=files, params=params)

        content_type, body = utils.encode_multipart_formdata(params, files)
        req = HTTPRequest(
            self.get_method_url('sendPhoto'),
            method="POST",
            headers={'Content-Type': content_type},
            body=body
        )
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

    @classmethod
    def get_file_url(cls, path, params=None):
        return 'https://api.telegram.org/file/bot' + cls.key + '/' + path

    @classmethod
    def get_method_url(cls, method, params=None):
        url = 'https://api.telegram.org/bot' + cls.key + '/' + method
        if params is not None:
            url = url_concat(url, params)
        return url

    @classmethod
    def get_webhook_url(cls):
        cls.access_key = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(30)])
        return options.server_schema + '://' + options.server_name + '/telegram.' + cls.access_key
