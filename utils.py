import discord
import sys

KATIE_USER_ID = 1302003829998358611
DAN_USER_ID = 406294459903377408


class CommandHandlers(object):
    def __init__(self, client: discord.Client):
        self.client = client

    @staticmethod
    async def hello_handler(message: discord.Message, *args):
        await message.channel.send("Hello!")

    async def quack_handler(self, message: discord.Message, *args):
        katie_user = self.client.get_user(KATIE_USER_ID)
        quack_message = f"Quack {katie_user.mention}"

        await message.channel.send(quack_message)
        await katie_user.send(quack_message)

    @staticmethod
    async def kill_handler(message: discord.Message, *args):
        if message.author.id != DAN_USER_ID:
            return

        sys.exit(12345)

    @staticmethod
    async def restart_handler(message: discord.Message, *args):
        if message.author.id != DAN_USER_ID:
            return

        sys.exit(0)