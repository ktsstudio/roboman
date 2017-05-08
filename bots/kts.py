from roboman.bot import BaseBot


class KTSBot(BaseBot):
    async def on_hook(self, data):
        await self.send('Hello!')
