import discord
from discord.ext import commands
import sys

KATIE_USER_ID = 1302003829998358611
DAN_USER_ID = 406294459903377408


class CommandHandlers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command(name="hello")
    async def hello_handler(self, ctx):
            await ctx.send("Hello!")

    @commands.command(name="kill")
    async def kill_handler(self, ctx):
        if ctx.author.id != DAN_USER_ID:
            return
        sys.exit(12345)
    
    @commands.command(name="restart")
    async def restart_handler(self, ctx):
        if ctx.author.id != DAN_USER_ID:
            return
        sys.exit(0)

    @commands.command(name="quack")
    async def quack_handler(self, ctx):
        katie_user = self._bot.get_user(KATIE_USER_ID)
        quack_message = f"Quack {katie_user.mention}"

        await ctx.send(quack_message)
        await katie_user.send(quack_message)


async def unimplemented_handler(*args):
    return None