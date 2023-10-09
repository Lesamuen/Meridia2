'''Module containing various functions related solely to electrum (per-user currency) management'''

from discord import ApplicationContext, Option
from discord import User as DiscordUser

from bot import bot_client, database_connector
from auxiliary import perms, log, get_time
from dbmodels import User

@bot_client.slash_command(name = "balance", description = "See how much electrum you currently own")
async def balance(context: ApplicationContext):
    '''
    Adds the command /balance
    '''

    log(get_time() + " >> " + str(context.author) + " queried their balance at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

    session = database_connector()

    user = User.find_user(session, context.author.id)
    await context.respond("You currently have **" + str(user.electrum) + "** electrum pieces.")

    session.close()

@bot_client.slash_command(name = "gift", description = "Send electrum to another user", guild_only = True)
async def gift(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to send electrum to", required = True),
    electrum: Option(int, description = "Amount to send", required = True, min_value = 0)
):
    '''
    Adds the command /gift
    '''

    log(get_time() + " >> " + str(context.author) + " sent " + str(electrum) + " electrum to " + str(user) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

    session = database_connector()

    sender = User.find_user(session, context.author.id)
    
    if electrum > sender.electrum:
        # If trying to send more money than user owns
        log("ERROR HAS OCCURRED   >> Not enough money!")
        await context.respond("You don't have that much money!")
    else:
        recipient = User.find_user(session, user.id)

        # Remove money from sender
        sender.add_electrum(session, -electrum)
        # Add money to recipient
        recipient.add_electrum(session, electrum)

        log("                     >> New balance of " + str(context.author) + " is " + str(sender.electrum))
        log("                     >> New balance of " + str(user) + " is " + str(recipient.electrum))
        await context.respond("Operation successful.")

    session.close()

@bot_client.slash_command(name = "rollcall", description = "Reward a user with 1 electrum for showing up at a session!", guild_only = True)
async def rollcall(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to reward", required = True)
):
    '''
    Adds the command /rollcall
    '''

    if context.author.id in perms["dm"]:
        log(get_time() + " >> DM " + str(context.author) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "] rollcalled " + str(user))
        
        session = database_connector()
        user_data = User.find_user(session, user.id)
        user_data.add_electrum(session, 1)
        log("                     >> New balance of " + str(user) + " is " + str(user_data.electrum))
        session.close()

        await context.respond(user.mention + " has been rewarded **1** electrum!")
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")