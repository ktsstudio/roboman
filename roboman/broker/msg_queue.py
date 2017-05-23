from collections import OrderedDict
from datetime import datetime

from roboman.bot.message import Message
from roboman.utils import now_ts
from tornado.locks import Condition
from tornado import gen


class MsgQueue(object):
    WORKER_DEAD_TIMEOUT = 5000  # 5 sec

    def __init__(self):
        self.condition = Condition()
        self.events_during_cycle = False

        self.locks = set()
        self.worker_locks = dict()
        self.queue = OrderedDict()
        self.last_queue_change = now_ts()

    def queue_iteration(self):
        queue_keys = list(self.queue.keys())
        queue_keys_iter = iter(queue_keys)

        return queue_keys, queue_keys_iter

    @gen.coroutine
    def next(self, worker_id, make_work=False):
        begin_time = now_ts()
        queue_keys, queue_keys_iter = self.queue_iteration()

        while True:
            try:
                key = next(queue_keys_iter)
                task = self.queue.get(key)

                if task and task.status == Message.STATUS_WORK:
                    flag = True

                    if flag and task.worker not in self.worker_locks:
                        flag = False
                    if flag and key not in self.worker_locks[task.worker]:
                        flag = False
                    if flag and now_ts() - self.worker_locks[task.worker][key] > self.WORKER_DEAD_TIMEOUT:
                        flag = False

                    if not flag:
                        task = self.make_new(key)

                if task and task.status == Message.STATUS_NEW and task.unique_key not in self.locks:
                    if callable(make_work):
                        make_work = make_work()

                    if make_work:
                        self.make_work(task.id, worker_id)

                    raise gen.Return(task)
            except StopIteration:
                if self.last_queue_change < begin_time:
                    yield self.condition.wait()

                begin_time = now_ts()
                queue_keys, queue_keys_iter = self.queue_iteration()

    def make_work(self, key, worker):
        if key in self.queue:
            if worker not in self.worker_locks:
                self.worker_locks[worker] = dict()

            self.locks.add(self.queue[key].unique_key)
            self.worker_locks[worker][key] = now_ts()

            self.queue[key].status = Message.STATUS_WORK
            self.queue[key].worker = worker

            self.notify()

    def make_new(self, key):
        if key in self.queue:
            worker = self.queue[key].worker

            if worker in self.worker_locks and key in self.worker_locks[worker]:
                del self.worker_locks[worker][key]
                if len(self.worker_locks[worker]) == 0:
                    del self.worker_locks[worker]

            if self.queue[key].unique_key in self.locks:
                self.locks.remove(self.queue[key].unique_key)

            self.queue[key].status = Message.STATUS_NEW
            self.queue[key].worker = None

            self.notify()

            return self.queue[key]

    def add(self, message):
        self.queue[message.id] = message
        self.notify()

    def remove(self, key, worker_id=None):
        if key in self.queue:
            item = self.queue[key]

            if worker_id in self.worker_locks and key in self.worker_locks[worker_id]:
                del self.worker_locks[worker_id][key]
            if item.unique_key in self.locks:
                self.locks.remove(item.unique_key)

            del self.queue[key]
            self.notify()

    def notify(self):
        self.last_queue_change = now_ts()
        self.condition.notify_all()

    def worker_locks_heartbeat(self, worker):
        if worker in self.worker_locks:
            now = now_ts()
            for key in self.worker_locks[worker].keys():
                self.worker_locks[worker][key] = now

    def stats(self):
        total = 0
        new = 0
        work = 0

        for key in list(self.queue.keys()):
            total += 1
            item = self.queue.get(key)

            if item and item.status == Message.STATUS_NEW:
                new += 1
            if item and item.status == Message.STATUS_WORK:
                work += 1

        return {
            'total': total,
            'new': new,
            'work': work,
        }


queue = MsgQueue()
buckets = dict()


def get_bucket(name):
    if name not in buckets:
        buckets[name] = MsgQueue()
    return buckets[name]
