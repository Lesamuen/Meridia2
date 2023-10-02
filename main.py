# Allows for other .py files to be found in /modules folder
from sys import path as syspath
syspath.append(syspath[0] + "\\modules")

# Load environment
import discord
from dotenv import load_dotenv
from os import system, getenv

load_dotenv(".env")
system("ffmpeg -version")
print("\nRunning PyCord version" + discord.__version__)
bot_token = getenv("BOTTOKEN")
if bot_token is None:
    print("Bot token not found!\nTerminating program...")
    quit()
else:
    print("Bot token found!\nLaunching Meridia...")

# Import all modules, setting up event listeners
from bot import bot_client
from auxiliary import log, getTime
import beacon

# Initialize bot loop
@bot_client.listen()
async def on_ready():
    log("\n" + getTime() + " >> Successfully logged in as " + str(bot_client.user))
@bot_client.listen()
async def on_disconnect():
    log("\n" + getTime() + " >> Lost connection to Discord!")

bot_client.run(bot_token)