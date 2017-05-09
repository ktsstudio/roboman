from roboman.bot.message import Message
import roboman.bot.request.vk
import roboman.bot.request.telegram


def send(msg, text):
    if msg.source == Message.SOURCE_VK:
        return vk.send(msg, text)
    elif msg.source == Message.SOURCE_TELEGRAM:
        return telegram.send(msg, text)
