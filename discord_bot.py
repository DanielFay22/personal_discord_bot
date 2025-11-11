import discord
from discord.ext import commands
import logging
from message_spammer import MessageSpammer
from utils import *
from random_chirps import RandomChirper
from knock_knock_jokes import JokeBot

with open("./token.txt") as f:
    TOKEN = f.read()

intents = discord.Intents.default()
intents.message_content = True # Required to read message content
intents.members = True # Required to read members of a server

COMMAND_PREFIX = '$'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

TARGET_USER_ID = KATIE_USER_ID

message_spammer = MessageSpammer(bot=bot, targeted_user_id=TARGET_USER_ID)
random_chirper = RandomChirper(bot=bot, target_user_id=TARGET_USER_ID)
command_handlers = CommandHandlers(bot=bot)
joke_handler = JokeBot(bot=bot, target_user_id=KATIE_USER_ID)

@bot.event
async def on_ready():
    await bot.add_cog(command_handlers)
    await bot.add_cog(random_chirper)
    await bot.add_cog(message_spammer)
    await bot.add_cog(joke_handler)

bot.run(TOKEN)