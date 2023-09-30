# Allows for other .py files to be found in /modules folder
from sys import path as syspath
syspath.append(syspath[0] + "\\modules")

# Load environment
import discord
from os import system, getenv
from dotenv import load_dotenv

load_dotenv("./.env")
system("ffmpeg -version")
print("\nRunning PyCord version" + discord.__version__)
bot_token = getenv("BOTTOKEN")
if bot_token is None:
    print("Bot token not found!\nTerminating program...")
    quit()

# Import all modules, setting up event listeners
from bot import bot_client
import auxilary

# Initialize bot loop
@bot_client.event
async def on_ready():
    print("\n" + auxilary.getTime() + ": " + "Successfully logged in as " + str(bot_client.user))

bot_client.run(bot_token)