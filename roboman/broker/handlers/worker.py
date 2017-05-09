from roboman.broker.handlers.base import BucketHandler
from tornado import gen


class WorkerHandler(BucketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.client_disconnected = False
        self.worker_id = None

    @property
    def get_methods(self):
        return {
            'get': self.get_message
        }

    @property
    def post_methods(self):
        return {
            'done': self.done_message,
            'heartbeat': self.heartbeat,
        }

    def done_message(self):
        task_id = self.get_str_argument('id')
        self.worker_id = self.get_str_argument('worker')

        self.bucket.remove(task_id, self.worker_id)
        self.send_success_response({'status': 'ok'})

    @gen.coroutine
    def get_message(self):
        self.worker_id = self.get_str_argument('worker')

        task = yield self.bucket.next(self.worker_id)

        if not self.client_disconnected:
            self.send_success_response(data=task.to_dict())
            self.flush()
        else:
            self.bucket.make_new(task.id, self.worker_id)

    def on_connection_close(self):
        super().on_connection_close()
        self.client_disconnected = True

    def heartbeat(self):
        worker_id = self.get_str_argument('worker')
        # print(worker_id)
