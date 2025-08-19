import discord
from discord.ext import tasks
import time


class HappyBirthday(object):
    message_text = [
        "Happy Birthday to you!",
        "Happy Birthday to you!",
        "Happy Birthday dear Katie!",
        "Happy Birthday to you!",
        "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉",
    ]

    def __init__(self, client: discord.Client, target_user_id: int):
        self.target_user = target_user_id
        self.client = client

        self.user = None
        self.get_user()

        self.running = False

    def get_user(self):
        self.user = self.client.get_user(self.target_user)

    async def start_happy_birthday(self, message: discord.Message, *args):
        if self.running:
            return
        if self.user is None:
            self.get_user()

        self.running = True
        self.send_message.start(message)

    async def stop_happy_birthday(self, message: discord.Message, *args):
        if not self.running:
            return

        self.running = False
        self.send_message.cancel()

    @tasks.loop(minutes=5)
    async def send_message(self, message: discord.Message):
        for line in self.message_text:
            await self.user.send(line)
            time.sleep(2)
