from collections import OrderedDict
from tornado import gen
from tornado.locks import Condition

STATUS_NEW = 'new'
STATUS_WORK = 'work'
STATUS_REMOVED = 'removed'


class Queue(object):
    def __init__(self):
        self.condition = Condition()
        self.events_during_cycle = False

        self.locks = set()
        self.worker_locks = dict()
        self.queue = OrderedDict()

        self.queue_keys = list()
        self.queue_keys_iter = None
        self.init_queue_iteration()

    def init_queue_iteration(self):
        self.queue_keys = list(self.queue.keys())
        self.queue_keys_iter = iter(self.queue_keys)
        self.events_during_cycle = False

    @gen.coroutine
    def next(self):
        while True:
            try:
                key = next(self.queue_keys_iter)
                item = self.queue.get(key)

                if item and item.get('status') == STATUS_NEW and item.unique_key not in self.locks:
                    raise gen.Return({'id': key, 'payload': item.get('payload')})
            except StopIteration:
                while not self.events_during_cycle:
                    yield self.condition.wait()
                self.init_queue_iteration()

    def make_work(self, key, worker_id):
        if key in self.queue:
            if worker_id not in self.worker_locks:
                self.worker_locks[worker_id] = set()

            self.locks.add(self.queue[key].unique_key)
            self.queue[key]['status'] = STATUS_WORK
            self.worker_locks[worker_id].add(key)

    def add(self, message):
        self.queue[message.id] = message

        self.queue_keys.append(message.id)
        self.notify()

    def remove(self, key, worker_id=None):
        if key in self.queue:
            item = self.queue[key]

            if worker_id in self.worker_locks and key in self.worker_locks[worker_id]:
                self.worker_locks[worker_id].remove(key)
            if item.unique_key in self.locks:
                self.locks.remove(item.unique_key)

            del self.queue[key]
            self.notify()

    def notify(self):
        self.events_during_cycle = True
        self.condition.notify()

    def stats(self):
        total = 0
        new = 0
        work = 0

        for key in list(self.queue.keys()):
            total += 1
            item = self.queue.get(key)

            if item and item.get('status') == STATUS_NEW:
                new += 1
            if item and item.get('status') == STATUS_WORK:
                work += 1

        return {
            'total': total,
            'new': new,
            'work': work,
        }


queue = Queue()
buckets = dict()


def get_bucket(name):
    if name not in buckets:
        buckets[name] = Queue()
    return buckets[name]
