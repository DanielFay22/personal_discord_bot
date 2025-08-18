
import discord
from discord.ext import tasks
import random
from enum import Enum
import logging

logger = logging.getLogger(__name__)

INITIAL_MESSAGE = "Knock, Knock"

KNOCK_KNOCK_INTERVAL_SEC = 5
REPEAT_INTERVAL_SEC = 30

jokes = [
    ("Atch", "Bless you!"),
]

class JokeState(Enum):
    INITIAL = 0
    JOKE = 1
    PUNCHLINE = 2
    END = 3



class JokeBot(object):
    def __init__(self, client: discord.Client, target_user_id: int):
        self.client = client
        self.target_user_id = target_user_id
        self.user = None

        self.running = False
        self.active_joke = random.randint(0, len(jokes))
        self.joke_state = JokeState.END


    async def set_target_user_handler(self, message: discord.Message, new_target_user_id: int, *args):
        self.target_user_id = new_target_user_id
        await message.channel.send(f"Updated target user to: {self.target_user_id}")


    async def joke_handler(self, message: discord.Message, *args):
        if self.running:
            # Handle joke update
            if self.joke_state == JokeState.INITIAL:
                # Message should roughly match "who's there"
                if message.content.lower().startswith("who's there"):
                    self.joke_state = JokeState.JOKE
                    self.joke_loop.change_interval(seconds=REPEAT_INTERVAL_SEC)
                return
            elif self.joke_state == JokeState.JOKE:
                # Message should roughly match <joke> who?
                if message.content.lower().startswith(jokes[self.active_joke][0].lower()):
                    self.joke_state = JokeState.PUNCHLINE
                return
            return
        else:
            self.active_joke = random.randint(0, len(jokes))
            self.running = True
            self.joke_state = JokeState.INITIAL
            self.joke_loop.change_interval(seconds=KNOCK_KNOCK_INTERVAL_SEC)
            self.joke_loop.start()

    async def stop_joke_handler(self, message: discord.Message, *args):
        if not self.running:
            return

        self.running = False
        self.joke_handler.cancel()

    @tasks.loop(seconds=5)
    async def joke_loop(self):
        user = self.client.get_user(self.target_user_id)

        if not user:
            logger.error("Could not find user, exiting")

        if self.joke_state == JokeState.INITIAL:
            await user.send(INITIAL_MESSAGE)
            return
        elif self.joke_state == JokeState.JOKE:
            await user.send(jokes[self.active_joke][0])
            return
        elif self.joke_state == JokeState.PUNCHLINE:
            await user.send(jokes[self.active_joke][1])
            self.joke_state = JokeState.END
            self.joke_loop.cancel()
            return
