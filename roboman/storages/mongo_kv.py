from datetime import datetime
from roboman.storages import BaseStorage
from mongoengine import connection


class MongoKV(BaseStorage):
    collection_name = '__mongo_kv_storage'

    def __init__(self, prefix=''):
        super().__init__()
        self._cache = {}
        self.collection_name = str(prefix) + self.collection_name

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    @property
    def db(self):
        return connection.get_db()

    @property
    def collection(self):
        return self.db[self.collection_name]

    def get(self, key, default=None):
        if key in self._cache:
            return self._cache[key]

        result = default

        record = self.collection.find_one({'key': key})
        if record:
            result = record.get('value', default)

        self._cache[key] = result
        return result

    def set(self, key, value, ttl=-1):
        data = {
            'key': key,
            'value': value,
            'ts': datetime.utcnow(),
            'ttl': ttl
        }

        self.collection.update({'key': key}, data, upsert=True)
        self._cache[key] = value

    def delete(self, key):
        self.collection.delete_many(dict(key=key))
        if key in self._cache:
            del self._cache[key]
