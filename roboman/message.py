import uuid


class Message(object):
    SOURCE_VK = 'vk'
    SOURCE_TELEGRAM = 'tg'

    def __init__(self, **kwargs):
        self.id = uuid.uuid4().hex
        self.worker = kwargs.get('worker')

        self.source = kwargs.get('source')
        self.user_id = kwargs.get('user_id')

        self.text = kwargs.get('text')
        self.extra = kwargs.get('extra') or dict()

    @property
    def unique_key(self):
        return '{0}:{1}'.format(self.source, self.user_id)

    def to_dict(self):
        result = dict()

        for key in ['id', 'worker', 'source', 'user_id', 'text', 'extra']:
            try:
                result[key] = getattr(self, key)
            except AttributeError:
                pass

        return result

    def from_dict(self, obj):
        for key in ['id', 'worker', 'source', 'user_id', 'text', 'extra']:
            setattr(self, key, obj.get(key))

    def __str__(self):
        return 'id={id}, worker={worker}, user={user}, extra={extra}'.format(
            id=self.id,
            worker=self.worker,
            user=self.unique_key,
            text=self.text,
            extra=str(self.extra),
        )
