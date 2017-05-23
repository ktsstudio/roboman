from roboman.broker.handlers.base import BrokerHandler
from tornado import gen


class WorkerHandler(BrokerHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.client_disconnected = False
        self.worker = None

    @property
    def get_methods(self):
        self.check_access_token()

        return {
            'get': self.get_message
        }

    @property
    def post_methods(self):
        self.check_access_token()

        return {
            'done': self.done_message,
            'heartbeat': self.heartbeat,
        }

    def done_message(self):
        task_id = self.get_str_argument('id')
        self.worker = self.get_str_argument('worker')

        self.bucket.remove(task_id, self.worker)
        self.send_success_response({'status': 'ok'})

    @gen.coroutine
    def get_message(self):
        def is_connected():
            return not self.client_disconnected

        self.worker = self.get_str_argument('worker')

        task = yield self.bucket.next(self.worker, is_connected)

        if is_connected():
            self.send_success_response(data=task.to_dict())
            self.flush()

        self.finish()

    def on_connection_close(self):
        super().on_connection_close()
        self.client_disconnected = True

    def heartbeat(self):
        self.worker = self.get_str_argument('worker')
        self.bucket.worker_locks_heartbeat(self.worker)
