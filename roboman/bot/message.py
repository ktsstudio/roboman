import uuid


class Message(object):
    SOURCE_VK = 'vk'
    SOURCE_TELEGRAM = 'tg'

    STATUS_NEW = 'new'
    STATUS_WORK = 'work'
    STATUS_REMOVED = 'removed'

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', uuid.uuid4().hex)
        self.status = kwargs.get('status', self.STATUS_NEW)
        self.worker = kwargs.get('worker')

        self.source = kwargs.get('source')
        self.from_id = kwargs.get('from_id')

        self.text = kwargs.get('text')
        self.extra = kwargs.get('extra') or dict()
        self.original = kwargs.get('original') or dict()
        self.credentials = kwargs.get('credentials') or dict()

    @property
    def unique_key(self):
        return '{0}:{1}'.format(self.source, self.from_id)

    def to_dict(self):
        result = dict()

        for key in ['id', 'worker', 'source', 'status', 'from_id', 'text', 'extra', 'credentials', 'original']:
            try:
                result[key] = getattr(self, key)
            except AttributeError:
                pass

        return result

    def from_dict(self, obj):
        for key in ['id', 'worker', 'source', 'status', 'from_id', 'text', 'extra', 'credentials', 'original']:
            setattr(self, key, obj.get(key))

    def __str__(self):
        return 'id={id}, worker={worker}, status={status}, user={user}, extra={extra}'.format(
            id=self.id,
            worker=self.worker,
            user=self.unique_key,
            status=self.status,
            text=self.text,
            extra=str(self.extra),
        )
