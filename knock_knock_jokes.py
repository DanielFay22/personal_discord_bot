
import discord
from discord.ext import tasks, commands
import random
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

INITIAL_MESSAGE = "Knock, Knock"

KNOCK_KNOCK_INTERVAL_SEC = 30

jokes = [
    ("Atch", "Bless you!"),
    ("Europe", "No, you're a poo!"),
    ("Boo", "you don't have to cry, it was only a joke..."),
    ("Lettuce", "Lettuce in, we're hungry!"),
    ("Yodelahee", "I didn't know you could yodel!"),
    ("Guess", "Is it Katie?"),
    ("Cargo", "Car go beep beep!"),
    ("Dwayne", "Dwayne dee badtub I'm dwoning!"),
    ("Hi", "Who is who?"),
    ("Owls", "Right"),
    ("Cows", "No, silly, cows moo. Owls who."),
    ("Monica", "Good job, Mr. President, just like we practiced"),
    ("The KGB", "*Slap* We will be the ones asking the questions!"),
    ("Candice", "Candice joke get any worse..."),
    ("I eat mop", "Ewww, you eat your poo?"),
    ("Panther", "Pather no path, I'm going thwimming!"),
    ("Spell", "W-H-O"),
    ("Daiy", "Daisy me rollin', they hatin'"),
    ("To", "No, it's \"*To whom*\""),
    ("Dishes", "Dishes Sean Connery"),
    ("Weave", "Weave been trying to reach you about your car's extended warranty."),
    ("Cash", "No thank you, I'm allergic to nuts."),
]

class JokeState(Enum):
    INITIAL = 0
    JOKE = 1
    PUNCHLINE = 2
    END = 3



class JokeBot(commands.Cog):
    _bot: commands.Bot

    _running: bool = False
    _user: discord.User = None
    _target_user_id: int

    _active_joke: int = random.randint(0, len(jokes) - 1)
    _joke_state: JokeState = JokeState.END

    def __init__(self, bot: commands.Bot, target_user_id: int):
        self._bot = bot
        self._target_user_id = target_user_id


    @staticmethod
    def clean_message(message: str):
        stripped_content = message.lower()
        stripped_content = re.sub(r'[^\w\s]','',stripped_content)
        return stripped_content

    @commands.command(name="joke_target_user")
    async def set_target_user_handler(self, ctx: commands.Context, new_target_user_id: int):
        self._target_user_id = new_target_user_id
        await ctx.send(f"Updated target user to: {self._target_user_id}")

    @commands.command(name="joke")
    async def joke_handler(self, ctx: commands.Context):
        if not self._running:
            self._active_joke = random.randint(0, len(jokes) - 1)
            self._running = True
            self._joke_state = JokeState.INITIAL

        # Handle joke update
        await self._handle_joke(ctx.message)

    @commands.command(name="joke_stop")
    async def stop_joke_handler(self, ctx: commands.Context):
        if not self._running:
            return

        self._running = False
        self._joke_state = JokeState.END

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self._bot.user.id:
            return
        if isinstance(message.channel, discord.DMChannel) and self._running:
            await self._handle_joke(message)

    async def _handle_joke(self, message: discord.Message):
        user = self._bot.get_user(self._target_user_id)

        if not user:
            logger.error("Could not find user, exiting")
        
        # First loop always sends "Knock, Knock"
        if self._joke_state == JokeState.INITIAL:
            logger.info("Sending initial knock knock message")
            self.spam_loop.start(user)
            self._joke_state = JokeState.JOKE
            return
        # Second loop sends the joke
        elif self._joke_state == JokeState.JOKE:
            if self.clean_message(message.content).startswith("whos there"):
                logger.info("Sending joke")
                self.spam_loop.cancel()
                self._joke_state = JokeState.PUNCHLINE
                await user.send(jokes[self._active_joke][0])
            else:
                logger.info(f"Invalid response: {message.content}")
            return
        # Third loop sends the punchline and ends the loop
        elif self._joke_state == JokeState.PUNCHLINE:
            if self.clean_message(message.content).startswith(jokes[self._active_joke][0].lower() + " who"):
                logger.info("Sending punchline")
                await user.send(jokes[self._active_joke][1])
                self._running = False
                self._joke_state = JokeState.END
            return

    @tasks.loop(seconds=KNOCK_KNOCK_INTERVAL_SEC)
    async def spam_loop(self, user: discord.User):
        logger.info("Sending knock knock message")
        await user.send(INITIAL_MESSAGE)
