
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
    ("Europe", "No, you're a poo!"),
    ("Boo", "you don't have to cry, it was only a joke...")
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
        self.active_joke = random.randint(0, len(jokes) - 1)
        self.joke_state = JokeState.END


    async def set_target_user_handler(self, message: discord.Message, new_target_user_id: int, *args):
        self.target_user_id = new_target_user_id
        await message.channel.send(f"Updated target user to: {self.target_user_id}")


    async def joke_handler(self, message: discord.Message, *args):
        if not self.running:
            self.active_joke = random.randint(0, len(jokes) - 1)
            self.running = True
            self.joke_state = JokeState.INITIAL
            await message.channel.send("Starting joke")

        # Handle joke update
        await self._handle_joke(message)


    async def stop_joke_handler(self, *args):
        if not self.running:
            return

        self.running = False
        self.joke_state = JokeState.END

    async def _handle_joke(self, message: discord.Message):
        user = self.client.get_user(self.target_user_id)

        if not user:
            logger.error("Could not find user, exiting")
        
        # First loop always sends "Knock, Knock"
        if self.joke_state == JokeState.INITIAL:
            self.spam_loop.start(user)
            self.joke_state = JokeState.JOKE
            return
        # Second loop sends the joke
        elif self.joke_state == JokeState.JOKE:
            if message.content.lower().startswith("who's there"):
                self.spam_loop.cancel()
                self.joke_state = JokeState.PUNCHLINE
                await user.send(jokes[self.active_joke][0])
            return
        # Third loop sends the punchline and ends the loop
        elif self.joke_state == JokeState.PUNCHLINE:
            if message.content.lower().startswith(jokes[self.active_joke][0].lower()):
                await user.send(jokes[self.active_joke][1])
                self.running = False
                self.joke_state = JokeState.END
            return

    @tasks.loop(seconds=KNOCK_KNOCK_INTERVAL_SEC)
    async def spam_loop(self, user: discord.User):
        await user.send(INITIAL_MESSAGE)
