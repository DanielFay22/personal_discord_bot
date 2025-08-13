import discord
from discord.ext import tasks
import logging

logger = logging.getLogger(__name__)

SPAM_MESSAGE_INTERVAL_SEC = 2

class MessageSpammer(object):
    initial_message = "Here come the ducks..."
    spam_message = "🐥"

    def __init__(self, client: discord.Client, targeted_user_id: int):
        self.client = client
        self.targeted_user_id = targeted_user_id
        self.user = None

        self.running = False
        self.message_count = 0

        self.message_queue = []

    def set_initial_message(self, new_message: str):
        self.initial_message = new_message

    async def set_spam_message(self, message: discord.Message, new_message: str, *args):
        self.spam_message = new_message
        await message.channel.send(f"Updated spam message to: {self.spam_message}")

    async def set_spam_interval_sec(self, message: discord.Message, new_interval: int|str, *args):
        if isinstance(new_interval, str):
            try:
                new_interval = int(new_interval)
            except ValueError:
                await message.channel.send("Invalid value provided, expect integer.")

        self.spam_loop.change_interval(seconds=new_interval)

        await message.channel.send(f"Successfully updated message interval to {new_interval} seconds")

    async def start(self, message: discord.Message, *args):
        if self.running:
            await message.channel.send("Already running")
        else:
            if self.user is None:
                self.find_user.start()
            else:
                self.spam_loop.start()
            self.running = True
            await message.channel.send("Started successfully")

    async def stop(self, message: discord.Message, *args):
        if not self.running:
            await message.channel.send("Already stopped")
        else:
            self.spam_loop.stop()
            self.find_user.stop()
            self.running = False
            await message.channel.send("Stopped successfully")

    async def set_new_target(self, message: discord.Message, new_target_user_id: int|str, *args):
        if isinstance(new_target_user_id, str):
            try:
                new_target_user_id = int(new_target_user_id)
            except ValueError:
                logger.error(f"Received invalid user id: {new_target_user_id}, ignoring input")
                await message.channel.send("Failed to update target user to requested ID")

        if self.spam_loop.is_running():
            self.spam_loop.stop()

        self.targeted_user_id = new_target_user_id

        # Start search for new user
        if self.running and not self.find_user.is_running():
            self.find_user.start()

        await message.channel.send("Successfully updated targeted user ID.")


    def find_user_helper(self):
        self.user = self.client.get_user(self.targeted_user_id)

        if self.running:
            if self.user:
                logger.info(f"Updating message target to {self.user.name}")

                # Make sure the spam message is running and user search is stopped
                if not self.spam_loop.is_running():
                    # Enqueue another initial message for new user
                    self.message_queue.append(self.initial_message)
                    self.spam_loop.start()
                    self.find_user.cancel()
                return
            else:
                # User couldn't be found, stop spam message and resume searching
                if self.spam_loop.is_running():
                    self.spam_loop.cancel()
                    self.find_user.start()
                logger.info("User not found, skipping task. Will retry in 60 seconds.")

    @tasks.loop(seconds=60.0)
    async def find_user(self):
        self.find_user_helper()

    @tasks.loop(seconds=SPAM_MESSAGE_INTERVAL_SEC)
    async def spam_loop(self):
        # Drain message queue
        while self.message_queue:
            await self.user.send(self.message_queue.pop(0))

        self.message_count += 1
        logger.info(f"Sending message, count: {self.message_count}")

        await self.user.send(self.spam_message)