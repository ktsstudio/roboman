from roboman.broker.queue import queue
from roboman.broker.handlers.base import BucketHandler
from roboman.message import Message
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
        msg = Message(self.get_payload())
        queue.remove(msg.id, msg.worker)
        self.send_success_response({'status': 'ok'})

    @gen.coroutine
    def get_message(self):
        self.worker_id = self.get_str_argument('worker')

        task = yield queue.next()
        response = Message(task)

        if not self.client_disconnected:
            self.send_success_response(data=response.to_dict())
            self.flush()
            queue.make_work(response.id, self.worker_id)

    def on_connection_close(self):
        super().on_connection_close()
        self.client_disconnected = True

    def heartbeat(self):
        worker_id = self.get_str_argument('worker')
        # print(worker_id)
