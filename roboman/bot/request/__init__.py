from roboman.bot.message import Message
import roboman.bot.request.vk
import roboman.bot.request.telegram


def send(bot, text):
    if bot.msg.source == Message.SOURCE_VK:
        try:
            url = bot.settings['api']['vk']
        except:
            url = None

        return vk.send(bot.msg, text, url=url, credentials=bot.credentials['vk'])
    elif bot.msg.source == Message.SOURCE_TELEGRAM:
        try:
            url = bot.settings['api']['tg']
        except:
            url = None

        return telegram.send(bot.msg, text, url=url, credentials=bot.credentials['telegram'])
