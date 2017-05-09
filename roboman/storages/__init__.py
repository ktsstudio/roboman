class BaseStorage(object):
    pass


class StoreSet(object):
    def __init__(self, stores=None):
        self.stores = stores if stores is not None else {}

    def __getattribute__(self, *args, **kwargs):
        store = super().__getattribute__('stores').get(args[0])
        if store is not None:
            return store
        return super().__getattribute__(*args, **kwargs)
