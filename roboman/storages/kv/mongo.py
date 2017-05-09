from datetime import datetime

from motor import MotorCollection
from roboman.storages import BaseStorage
import motor
from tornado import gen


class Store(BaseStorage):
    def __init__(self, **kwargs):
        super().__init__()
        self._cache = {}

        self.client = motor.motor_tornado.MotorClient(kwargs['uri'])
        self.db = self.client[kwargs['db']]

        self.collection_name = self.__module__ + "." + self.__class__.__name__
        if kwargs.get('prefix'):
            self.collection_name = '{0}:{1}'.format(kwargs.get('prefix'), self.collection_name)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    @property
    def collection(self):
        return self.db[self.collection_name]

    async def get(self, key, default=None):
        if key in self._cache:
            return self._cache[key]

        result = default

        record = await self.collection.find_one({'key': key})
        if record:
            result = record.get('value', default)

        self._cache[key] = result
        return result

    async def set(self, key, value, ttl=-1):
        data = {
            'key': key,
            'value': value,
            'ts': datetime.utcnow(),
            'ttl': ttl
        }

        await self.collection.update_one({'key': key}, {'$set': data}, upsert=True)
        self._cache[key] = value

    async def delete(self, key):
        await self.collection.delete_many(dict(key=key))
        if key in self._cache:
            del self._cache[key]
