from tornkts import utils


class Keyboard(object):
    def to_dict(self):
        raise NotImplemented

    def to_json(self):
        return utils.json_dumps(self.to_dict())

    def __str__(self):
        return self.to_json()

    def __unicode__(self):
        return self.to_json()


class ReplyKeyboard(Keyboard):
    def __init__(self, **kwargs):
        self.keyboard = kwargs.get('keyboard', [])
        self.resize_keyboard = kwargs.get('resize_keyboard', True)
        self.one_time_keyboard = kwargs.get('one_time_keyboard', True)
        self.selective = kwargs.get('selective', False)

    def to_dict(self):
        return {
            'keyboard': self.keyboard,
            'resize_keyboard': self.resize_keyboard,
            'one_time_keyboard': self.one_time_keyboard,
            'selective': self.selective
        }


class InlineKeyboard(Keyboard):
    def __init__(self, **kwargs):
        self.inline_keyboard = kwargs.get('keyboard', [])
        self.resize_keyboard = kwargs.get('resize_keyboard', True)
        self.one_time_keyboard = kwargs.get('one_time_keyboard', True)
        self.selective = kwargs.get('selective', False)

    def to_dict(self):
        keyboard = self.inline_keyboard
        for i, row in enumerate(keyboard):
            for j, button in enumerate(row):
                keyboard[i][j] = button.to_dict()

        return {
            'inline_keyboard': keyboard
        }


class ReplyKeyboardHide(ReplyKeyboard):
    def __init__(self, **kwargs):
        super(ReplyKeyboardHide, self).__init__(**kwargs)
        self.hide_keyboard = kwargs.get('hide_keyboard', True)
        self.selective = kwargs.get('selective', False)

    def to_dict(self):
        data = super(ReplyKeyboardHide, self).to_dict()
        data.update({
            'hide_keyboard': self.hide_keyboard,
            'selective': self.selective
        })
        return data


class KeyboardButton(Keyboard):
    def __init__(self, **kwargs):
        self.text = kwargs.get('text', '')
        self.request_contact = kwargs.get('request_contact', False)
        self.request_location = kwargs.get('request_location', False)

    def to_dict(self):
        return {
            'text': self.text,
            'request_contact': self.request_contact,
            'request_location': self.request_location,
        }


class InlineKeyboardButton(Keyboard):
    def __init__(self, **kwargs):
        self.text = kwargs.get('text', '')
        self.url = kwargs.get('url', False)
        self.callback_data = kwargs.get('callback_data', False)
        self.switch_inline_query = kwargs.get('switch_inline_query', False)

    def to_dict(self):
        result = {
            'text': self.text
        }

        if self.url:
            result['url'] = self.url
        if self.switch_inline_query:
            result['switch_inline_query'] = self.switch_inline_query
        if self.callback_data:
            result['callback_data'] = self.callback_data

        return result
