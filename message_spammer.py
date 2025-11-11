from discord.ext import tasks, commands
import logging

logger = logging.getLogger(__name__)

SPAM_MESSAGE_INTERVAL_SEC = 2

class MessageSpammer(commands.Cog):
    initial_message = "Here come the ducks..."
    spam_message = "🐥"

    _bot: commands.Bot
    _running: bool = False

    _message_count: int = 0

    def __init__(self, bot: commands.Bot, targeted_user_id: int):
        self._bot = bot
        self.targeted_user_id = targeted_user_id
        self.user = None

        self.message_queue = []

    def set_initial_message(self, new_message: str):
        self.initial_message = new_message

    @commands.command(name="set_message")
    async def set_spam_message(self, ctx: commands.Context, new_message: str):
        self.spam_message = new_message
        await ctx.send(f"Updated spam message to: {self.spam_message}")

    @commands.command(name="set_interval")
    async def set_spam_interval_sec(self, ctx: commands.Context, new_interval: int):
        self.spam_loop.change_interval(seconds=new_interval)

        await ctx.send(f"Successfully updated message interval to {new_interval} seconds")

    @commands.command(name="start")
    async def start(self, ctx: commands.Context):
        if self._running:
            await ctx.send("Already running")
        else:
            if self.user is None:
                self.find_user.start()
            else:
                self.spam_loop.start()
            self._running = True
            await ctx.send("Started successfully")

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        if not self._running:
            await ctx.send("Already stopped")
        else:
            self.spam_loop.stop()
            self.find_user.stop()
            self._running = False
            await ctx.send("Stopped successfully")

    @commands.command(name="target_user")
    async def set_new_target(self, ctx: commands.Context, new_target_user_id: int):
        if self.spam_loop.is_running():
            self.spam_loop.stop()

        self.targeted_user_id = new_target_user_id

        # Start search for new user
        if self._running and not self.find_user.is_running():
            self.find_user.start()

        await ctx.send("Successfully updated targeted user ID.")


    def find_user_helper(self):
        self.user = self._bot.get_user(self.targeted_user_id)

        if self._running:
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

        self._message_count += 1
        logger.info(f"Sending message, count: {self._message_count}")

        await self.user.send(self.spam_message)