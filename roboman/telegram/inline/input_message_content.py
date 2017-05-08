from tornkts import utils


class InputMessageContent(object):
    def to_dict(self):
        raise NotImplemented

    def to_json(self):
        return utils.json_dumps(self.to_dict())

    def __str__(self):
        return self.to_json()

    def __unicode__(self):
        return self.to_json()


class InputTextMessageContent(InputMessageContent):
    def __init__(self, message_text=None, parse_mode='Markdown', disable_web_page_preview=False):
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview

    def to_dict(self):
        return {
            'message_text': self.message_text,
            'parse_mode': self.parse_mode,
            'disable_web_page_preview': self.disable_web_page_preview,
        }
