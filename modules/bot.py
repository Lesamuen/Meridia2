'''Contains global bot object'''

import discord
import discord.ext.commands as discomm

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_client = discomm.Bot(intents = intents)