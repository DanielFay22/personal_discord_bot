from discord.ext import tasks, commands
import argparse
import random
import logging

logger = logging.getLogger(__name__)

class RandomChirper(object):
    _running: bool = False
    _bot: commands.Bot

    def __init__(
            self,
            bot: commands.Bot,
            target_user_id: int,
            min_interval_sec: int = 10,
            max_interval_sec: int = 3600,
    ):
        self._bot = bot

        self.min_interval = min_interval_sec
        self.max_interval = max_interval_sec

        self.message = ""

        self.target_user_id = target_user_id

        self.author_id = 0

    def get_new_interval(self) -> int:
        return random.randint(self.min_interval, self.max_interval)

    @commands.command(name="chirp_debug")
    async def debug_chirp_handler(self, ctx):
        if self._running:
            await ctx.send(
                f"Active chirp from user {self.author_id} targeting {self.target_user_id}. "
                f"Message: {self.message} - Frequency range: {self.min_interval}-{self.max_interval}"
            )
        else:
            await ctx.send(f"No chirp active.")

    @commands.command(name="chirp_start")
    async def start_chirp_handler(self, ctx, *args):
        if self._running:
            await ctx.send("Already running chirp")

        self.start_chirp_parse_args(*args)

        self.send_chirp.change_interval(seconds=self.get_new_interval())
        self.send_chirp.start()
        self._running = True
        self.author_id = ctx.author.id

        await ctx.send(f"Chirp started targeting user {self.target_user_id}")

    @commands.command(name="chirp_stop")
    async def stop_chirp_handler(self, ctx):
        if not self._running:
            await ctx.send("Already stopped")

        if self.author_id and self.author_id != ctx.author.id:
            await ctx.send("Operation not authorized")
            return

        self.send_chirp.stop()
        self._running = False
        self.author_id = 0

        await ctx.send("Successfully stopped chirp process.")

    @tasks.loop(seconds=60)
    async def send_chirp(self):
        user = self._bot.get_user(self.target_user_id)
        if user:
            await user.send(self.message)

        new_interval = self.get_new_interval()
        self.send_chirp.change_interval(seconds=new_interval)

        logger.info(f"New interval set to {new_interval}")


    def start_chirp_parse_args(self, *args) -> None:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("target_user_id", type=int)
        parser.add_argument("--min-interval", type=int, default=self.min_interval)
        parser.add_argument("--max-interval", type=int, default=self.max_interval)
        parser.add_argument("message", type=str, nargs='+'),

        res = parser.parse_args(args)

        self.target_user_id = res.target_user_id
        self.message = " ".join(res.message)
        self.min_interval = res.min_interval
        self.max_interval = res.max_interval
