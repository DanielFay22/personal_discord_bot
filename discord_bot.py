import discord
from discord.ext import commands
import logging
from message_spammer import MessageSpammer
from utils import *
from random_chirps import RandomChirper
from knock_knock_jokes import JokeBot

with open("./token.txt") as f:
    TOKEN = f.read()

COMMAND_PREFIX = '$'

intents = discord.Intents.default()
intents.message_content = True # Required to read message content
intents.members = True # Required to read members of a server

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

TARGET_USER_ID = KATIE_USER_ID

message_spammer = MessageSpammer(bot=bot, targeted_user_id=TARGET_USER_ID)
random_chirper = RandomChirper(bot=bot, target_user_id=TARGET_USER_ID)
command_handlers = CommandHandlers(bot=bot)
joke_handler = JokeBot(bot=bot, target_user_id=KATIE_USER_ID)

bot.add_command(hello_handler)
bot.add_command(command_handlers.quack_handler)

# Operational commands
bot.add_command(kill_handler)
bot.add_command(restart_handler)

# Chirp commands
bot.add_command(random_chirper.start_chirp_handler)
bot.add_command(random_chirper.stop_chirp_handler)
bot.add_command(random_chirper.debug_chirp_handler)

# Spam commands
bot.add_command(message_spammer.start)
bot.add_command(message_spammer.stop)
bot.add_command(message_spammer.set_new_target)
bot.add_command(message_spammer.set_spam_message)
bot.add_command(message_spammer.set_spam_interval_sec)

# Joke commands
bot.add_command(joke_handler.joke_handler)
bot.add_command(joke_handler.stop_joke_handler)
bot.add_command(joke_handler.set_target_user_handler)

bot.run(TOKEN)