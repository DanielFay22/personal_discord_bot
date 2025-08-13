import discord
from discord.ext import tasks
import argparse
import random
import logging

logger = logging.getLogger(__name__)

class RandomChirper(object):

    def __init__(
            self,
            client: discord.Client,
            target_user_id: int,
            min_interval_sec: int = 10,
            max_interval_sec: int = 3600,
    ):
        self.client = client

        self.running = False

        self.min_interval = min_interval_sec
        self.max_interval = max_interval_sec

        self.message = ""

        self.target_user_id = target_user_id

    def get_new_interval(self) -> int:
        return random.randint(self.min_interval, self.max_interval)

    async def start_chirp_handler(self, message: discord.Message, *args):
        if self.running:
            await message.channel.send("Already running chirp")

        self.start_chirp_parse_args(*args)

        self.send_chirp.change_interval(seconds=self.get_new_interval())
        self.send_chirp.start()
        self.running = True

        await message.channel.send(f"Chirp started targeting user {self.target_user_id}")

    async def stop_chirp_handler(self, message: discord.Message, *args):
        if not self.running:
            await message.channel.send("Already stopped")

        self.send_chirp.stop()
        self.running = False

        await message.channel.send("Successfully stopped chirp process.")

    @tasks.loop(seconds=60)
    async def send_chirp(self):
        user = self.client.get_user(self.target_user_id)
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
