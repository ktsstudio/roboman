from hashlib import md5
from datetime import datetime
from tornkts import utils


class InlineQueryResult(object):
    def __init__(self, **params):
        self.params = params

    def to_dict(self):
        params = {}
        for key, value in self.params.items():
            if value is not None:
                params[key] = value
        return params

    def to_json(self):
        return utils.json_dumps(self.to_dict())

    def __str__(self):
        return self.to_json()

    def __unicode__(self):
        return self.to_json()


class InlineQueryResultArticle(InlineQueryResult):
    def __init__(self, **params):
        super().__init__(**params)

        if self.params.get('id') is None:
            self.params['id'] = md5(str(datetime.now().timestamp()).encode('utf-8')).hexdigest()

        if self.params.get('input_message_content') is None:
            self.params['input_message_content'] = {}

    def to_dict(self):
        params = super().to_dict()
        params['type'] = 'article'
        return params
