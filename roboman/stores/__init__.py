import weakref


class BaseStore(object):
    def __init__(self, **kwargs):
        self._store = kwargs.get('stores')

    @property
    def store(self):
        if isinstance(self._store, weakref.ref):
            return self._store()
        return self._store


class StoreSet(object):
    def __init__(self, stores=None):
        self.stores = stores if stores is not None else {}

    def __setitem__(self, key, value):
        self.stores[key] = value

    def __setattr__(self, key, value):
        if key == 'stores':
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getattribute__(self, *args, **kwargs):
        key = args[0]
        if key == 'stores':
            return super().__getattribute__(*args, **kwargs)

        store = super().__getattribute__('stores').get(key)
        if store is not None:
            return store
        return super().__getattribute__(*args, **kwargs)
