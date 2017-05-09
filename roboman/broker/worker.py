from roboman.bot.bot import BaseBot
from roboman.bot.message import Message
from roboman.log import get_logger
from roboman.storages import StoreSet
from tornkts import utils
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from urllib import parse
from tornado import gen
from tornado.ioloop import IOLoop
import uuid


class Worker(object):
    def __init__(self, **kwargs):
        self.broker_url = kwargs.get('broker_url', 'http://127.0.0.1:5555')
        self.bucket = kwargs.get('bucket', 'main')
        self.bot = kwargs.get('bot')

        self.worker_id = 'worker-{0}'.format(uuid.uuid4().hex)
        self.logger = get_logger('worker')
        self.client = AsyncHTTPClient()

        store = dict()
        for name, params in kwargs.get('stores', {}).items():
            try:
                module_name, class_name = params['class'].rsplit('.', 1)
                module_instance = __import__(module_name, fromlist=[class_name])
                store[name] = getattr(module_instance, class_name)(**params)
            except Exception as e:
                pass
                # self.logger.exception(e)

        self.store = StoreSet(store)

    def start(self, loop=None):
        loop = loop or IOLoop.instance()
        if not self.bot or not issubclass(self.bot, BaseBot):
            raise Exception('Bot not setup')

        loop.add_callback(self.receiver)
        loop.add_callback(self.heartbeat)

    def method(self, method, params=None):
        result = '{url}/{bucket}/worker.{method}'.format(
            url=self.broker_url,
            bucket=self.bucket,
            method=method
        )

        if params:
            result = '{0}?{1}'.format(result, parse.urlencode(params))

        return result

    @gen.coroutine
    def process_message(self, **kwargs):
        msg = kwargs['msg']
        success = False

        self.logger.info('Start task id={0}'.format(msg.id))
        try:
            bot = self.bot(msg, store=self.store)
            try:
                yield bot.run()
            except Exception as e:
                self.logger.exception(e)
                yield bot.send('Произошла ошибка')
        except:
            pass
        self.logger.info('Finish task id={0}'.format(msg.id))

        request = HTTPRequest(
            self.method('done'),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=utils.json_dumps({'worker': self.worker_id, 'id': msg.id}),
            request_timeout=60
        )

        while not success:
            try:
                yield self.client.fetch(request)
                success = True
            except Exception as e:
                self.logger.error('Error on send about done {0} ({1}), retry'.format(msg.id, str(e)))
                yield gen.sleep(0.1)

    @gen.coroutine
    def receiver(self):
        while True:
            request = HTTPRequest(self.method('get', {'worker': self.worker_id}), request_timeout=60)

            try:
                self.logger.info('Fetch task from broker')
                response = yield self.client.fetch(request)
                data = utils.json_loads(response.body)

                if data and data.get('data'):
                    msg = Message(**data.get('data'))
                    self.logger.info('Fetched task id={0}'.format(msg.id))
                    IOLoop.instance().add_callback(self.process_message, msg=msg)
            except ConnectionRefusedError:
                self.logger.warning('Broker refuse connection, retry in 1 second...')
                yield gen.sleep(1)
            except HTTPError as e:
                if e.code == 599:
                    self.logger.warning('Long-poll fetch timeout')
                else:
                    self.logger.error(e.message)
                    yield gen.sleep(0.5)
            except Exception as e:
                self.logger.error(str(e))

    @gen.coroutine
    def heartbeat(self):
        while True:
            request = HTTPRequest(
                self.method('heartbeat'),
                method='POST',
                body=parse.urlencode(dict(worker=self.worker_id)),
                request_timeout=1
            )

            try:
                yield self.client.fetch(request)
            except:
                pass
            finally:
                yield gen.sleep(1)


if __name__ == '__main__':
    loop = IOLoop.instance()

    worker = Worker()
    worker.start()
    loop.start()
