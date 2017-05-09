from roboman.broker.msg_queue import get_bucket
from tornkts import utils
from tornkts.base.server_response import ServerError
from tornkts.handlers import BaseHandler


class BucketHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._payload = None
        self._bucket = None

    @property
    def bucket(self):
        return get_bucket(self._bucket)

    @property
    def bucket_name(self):
        return self._bucket

    def set_bucket(self, bucket):
        self._bucket = bucket

    def get(self, *args, **kwargs):
        if len(args) > 0:
            self.set_bucket(args[0])
            args = args[1:]
        else:
            raise ServerError(ServerError.BAD_REQUEST, description='bucket_undefined')

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if len(args) > 0:
            self.set_bucket(args[0])
            args = args[1:]
        else:
            raise ServerError(ServerError.BAD_REQUEST, description='bucket_undefined')

        return super().post(*args, **kwargs)

    def get_payload(self):
        if self._payload is None:
            try:
                self._payload = utils.json_loads(self.request.body.decode())
            except:
                pass

        return self._payload

    def get_argument(self, name, default=BaseHandler._ARG_DEFAULT, strip=True, **kwargs):
        if self.request.method == 'POST':
            payload = self.get_payload()

            if payload and name in payload:
                return payload[name]
            else:
                return super(BaseHandler, self).get_argument(name, default, strip)
        else:
            return super(BaseHandler, self).get_argument(name, default, strip)
