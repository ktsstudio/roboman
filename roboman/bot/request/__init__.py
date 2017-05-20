from roboman.bot.message import Message
import roboman.bot.request.vk
import roboman.bot.request.telegram


def get_url(bot):
    if bot.msg.source == Message.SOURCE_VK:
        try:
            return bot.settings['api']['vk']
        except:
            return None
    elif bot.msg.source == Message.SOURCE_TELEGRAM:
        try:
            return bot.settings['api']['tg']
        except:
            return None

    return None


async def send(bot, text):
    if bot.msg.source == Message.SOURCE_VK:
        return await vk.send(bot.msg, text, url=get_url(bot), credentials=bot.credentials['vk'])
    elif bot.msg.source == Message.SOURCE_TELEGRAM:
        return await telegram.send(bot.msg, text, url=get_url(bot), credentials=bot.credentials['telegram'])


def send_image(bot, path):
    if bot.msg.source == Message.SOURCE_VK:
        return vk.send_image(bot.msg, path, url=get_url(bot), credentials=bot.credentials['vk'])
    elif bot.msg.source == Message.SOURCE_TELEGRAM:
        return telegram.send_image(bot.msg, path, url=get_url(bot), credentials=bot.credentials['telegram'])
