from roboman.bot.bot import BaseBot


class KTSBot(BaseBot):
    async def hook(self):
        await self.send('Hello!')
