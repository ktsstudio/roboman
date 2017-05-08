import sys
from roboman.broker.handlers.base import BucketHandler
from roboman.message import Message
from tornkts.base.server_response import ServerError


class HookHandler(BucketHandler):
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
        message = self.get_payload()

        if message.get('type') == 'confirmation':
            self.write(vk.get('confirmation'))
        elif message.get('type') == 'message_new':
            group_id = message.get('group_id')
            flag = False

            for item in vk.get('communities'):
                if item.get('id') == group_id:
                    flag = True

            if not flag:
                raise ServerError(ServerError.ACCESS_DENIED, description='unknown_group_id')

        payload = self.get_payload()

        try:
            msg = Message(**{
                'source': Message.SOURCE_VK,
                'user_id': payload['object']['user_id'],
                'text': payload['object']['body'],
                'extra': {
                    'group_id': payload['group_id']
                }
            })

            self.bucket.add(msg)
            self.send_success_response({'status': 'ok'})
        except KeyError:
            self.send_error(ServerError.BAD_REQUEST)

    def telegram(self):
        telegram = self.application.get_messenger_settings('telegram')

        payload = self.get_payload()
        print(payload)
        sys.exit(1)

        msg = Message(self.get_payload())
        self.bucket.add(msg)
        self.send_success_response({'status': 'ok'})
