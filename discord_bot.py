import discord
import logging
from message_spammer import MessageSpammer
from utils import KATIE_USER_ID, DAN_USER_ID, CommandHandlers

with open("./token.txt") as f:
    TOKEN = f.read()

intents = discord.Intents.default()
intents.message_content = True # Required to read message content
intents.members = True # Required to read members of a server

client = discord.Client(intents=intents)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

TARGET_USER_ID = KATIE_USER_ID

message_spammer = MessageSpammer(client=client, targeted_user_id=TARGET_USER_ID)
command_handlers = CommandHandlers(client=client)

COMMAND_PREFIX = '$'
COMMANDS = {
    'hello': CommandHandlers.hello_handler,
    'start': message_spammer.start,
    'stop': message_spammer.stop,
    'target_user': message_spammer.set_new_target,
    'set_message': message_spammer.set_spam_message,
    'quack': command_handlers.quack_handler,
}

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # Handle command input
    if message.content.startswith(COMMAND_PREFIX):
        split_msg = message.content.split()

        command_str = split_msg.pop(0)[1:]
        if command_str in COMMANDS:
            await COMMANDS[command_str](message, *split_msg)
        else:
            await message.channel.send("Unrecognized Command")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


client.run(TOKEN)
