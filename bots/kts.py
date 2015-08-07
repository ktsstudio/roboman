# coding=utf-8
import random
import requests
from roboman import BaseBot
from py_expression_eval import Parser


class KTSBot(BaseBot):
    name = 'kts'
    key = '116835760:AAGuIPvUFUhAdEYpXD2QFHS04o4-h4DjF30'

    allowed_chats = [-23165158, 100538095, 1012824]

    @classmethod
    def on_hook(cls, data):
        chat_id = data.get('chat_id')
        print chat_id
        if chat_id in cls.allowed_chats:
            text = data.get('text')
            text = text.strip()

            if text.startswith('@KTSBot'):
                text = text[len('@KTSBot'):]
                text = text.strip()
            print text

            response = ''
            if text.startswith('/serega'):
                var = random.choice([u'мороженое', u'шашлыки', u'чебуреки', u'пицца'])
                response = u'У Сереги в Анапе %s, можно от качалки отдохнуть!' % (var,)
            elif text.startswith('/max'):
                var = random.choice(
                    [u'за косарь', u'это еще месяц', u'это за 20 тысяч можно', u' за два вечера бахнем'])
                response = u'Ну %s.' % (var)
            elif text.startswith('/calc'):
                parser = Parser()
                text = text[len('/calc'):]
                try:
                    response = parser.evaluate(text, {})
                except:
                    response = u'Пока считала, ошиблась'
            else:
                response = u'Извините, не знаю'

            r = requests.post(cls.get_method_url('sendMessage'), {'chat_id': chat_id, 'text': response})
        else:
            r = requests.post(cls.get_method_url('sendMessage'),
                              {'chat_id': chat_id, 'text': u'Извините, это закрытый бот'})
