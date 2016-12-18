from tornkts import utils
from tornkts.base.server_response import ServerError
from tornkts.handlers import BaseHandler

__author__ = 'grigory51'


class WebHookHandler(BaseHandler):
    def post(self, access_key):
        bots = self.settings.get('bots', [])
        ok = False
        for bot in bots:
            if bot.access_key == access_key:
                ok = True
                data = utils.json_loads(self.request.body)
                bot = bot()
                bot.on_hook(**data)
                break
        if ok:
            self.send_success_response()
        else:
            raise ServerError('not_found')
