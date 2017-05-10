import sys
from roboman.broker.handlers.base import BrokerHandler
from roboman.bot.message import Message
from tornkts.base.server_response import ServerError


class HookHandler(BrokerHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @property
    def post_methods(self):
        return {
            'vk': self.vk,
            'telegram': self.telegram,
        }

    def vk(self):
        vk = self.application.get_messenger_settings('vk')
        bot = vk.get('bots').get(self.bucket_name)

        if not bot:
            raise ServerError(ServerError.ACCESS_DENIED, description='unknown_bot')

        message = self.get_payload()

        if message.get('type') == 'confirmation':
            self.write(bot.get('confirmation'))
        elif message.get('type') == 'message_new':
            group_id = message.get('group_id')

            if bot.get('id') != group_id:
                raise ServerError(ServerError.ACCESS_DENIED, description='unknown_group_id')

            payload = self.get_payload()

            try:
                msg = Message(**{
                    'source': Message.SOURCE_VK,
                    'from_id': payload['object']['user_id'],
                    'text': payload['object']['body'],
                    'extra': {
                        'group_id': payload['group_id']
                    },
                    'original': dict(payload),
                    'credentials': bot,
                })

                self.bucket.add(msg)
                self.write('ok')
            except KeyError:
                self.send_error(ServerError.BAD_REQUEST)

    def telegram(self):
        telegram = self.application.get_messenger_settings('telegram')
        bot = telegram.get('bots').get(self.bucket_name)

        if not bot:
            raise ServerError(ServerError.ACCESS_DENIED, description='unknown_bot')

        payload = self.get_payload()

        try:
            msg = Message(**{
                'source': Message.SOURCE_TELEGRAM,
                'from_id': payload['message']['chat']['id'],
                'text': payload['message']['text'],
                'extra': {
                    'from': payload['message']['from']
                },
                'original': dict(payload),
                'credentials': bot,
            })

            self.bucket.add(msg)
            self.send_success_response({'status': 'ok'})
        except KeyError:
            # skip unsupported message
            self.send_success_response({'status': 'ok'})
