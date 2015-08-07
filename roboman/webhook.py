from tornkts.base.server_response import ServerError

__author__ = 'grigory51'
from tornkts.handlers import BaseHandler


class WebHookHandler(BaseHandler):
    def post(self, id):
        bots = self.settings.get('bots', [])
        ok = False
        for bot in bots:
            if bot.access_key == id:
                ok = True
                bot._on_hook(self.request.body)
                break
        if ok:
            self.send_success_response()
        else:
            raise ServerError('not_found')
