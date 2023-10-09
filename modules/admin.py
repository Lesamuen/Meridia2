'''Contains several bot commands for admining or debugging'''

from discord import ApplicationContext, Option
from discord import User as DiscordUser

from bot import bot_client, database_connector
from auxiliary import perms, log, get_time

from dbmodels import User

admin_cmds = bot_client.create_group("admin", "Commands to affect behind the scenes stuff for Meridia")

@admin_cmds.command(name = "pineapple", description = "Shuts down bot externally")
async def admin_pineapple(context: ApplicationContext):
    '''
    Adds the command /admin pineapple
    '''

    if context.author.id in perms["admin"]:
        await context.respond("change da world\nmy final message. Goodb ye.")
        log(get_time() + " >> Admin " + str(context.author) + " externally shut down Meridia from GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")
        await bot_client.close()
        quit()
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

@admin_cmds.command(name = "setdbprog", description = "Set a user's Dawnbreaker quest progress")
async def admin_setdbprog(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to edit", required = True),
    progress: Option(int, description = "Number between -1 and 20 to set to", required = True, min_value = -1, max_value = 20)
):
    '''
    Adds the command /admin setdbprog
    '''

    if context.author.id in perms["admin"]:
        log(get_time() + " >> Admin " + str(context.author) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "] is setting Dawnbreaker progress of " + str(user) + " to " + str(progress))
        
        session = database_connector()
        user_data = User.find_user(session, user.id)
        user_data.dawnbreaker(session, progress)
        session.close()

        await context.respond("Operation complete")
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

@admin_cmds.command(name = "resetcd", description = "Reset a user's beacon touching cooldown")
async def admin_resetcd(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to reset cooldown for", required = True)
):
    '''
    Adds the command /admin resetcd
    '''

    if context.author.id in perms["admin"]:
        log(get_time() + " >> Admin " + str(context.author) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "] is disabling beacon touch cooldown of " + str(user))
        
        session = database_connector()
        user_data = User.find_user(session, user.id)
        user_data.reset_cd(session)
        session.close()

        await context.respond("Operation complete")
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

@admin_cmds.command(name = "setcurrency", description = "Set a user's balance of electrum")
async def admin_setcurrency(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to set the electrum of", required = True),
    electrum: Option(int, description = "Positive number to set balance to", required = True, min_value = 0)
):
    '''
    Adds the command /admin setcurrency
    '''

    if context.author.id in perms["admin"]:
        log(get_time() + " >> Admin " + str(context.author) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "] set balance of " + str(user) + " to " + str(electrum))
        
        session = database_connector()
        user_data = User.find_user(session, user.id)
        user_data.add_electrum(session, electrum - user_data.electrum)
        session.close()

        await context.respond("Operation complete")
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")

@admin_cmds.command(name = "getcurrency", description = "Get a user's balance of electrum")
async def admin_getcurrency(
    context: ApplicationContext,
    user: Option(DiscordUser, description = "Discord user to get the electrum of", required = True)
):
    '''
    Adds the command /admin getcurrency
    '''

    if context.author.id in perms["admin"]:
        log(get_time() + " >> Admin " + str(context.author) + " at GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "] queried balance of " + str(user))
        
        session = database_connector()
        user_data = User.find_user(session, user.id)
        await context.respond("Current Electrum: " + str(user_data.electrum))
        session.close()
    else:
        await context.respond("I don't know you, and I don't care to know you.")
        log(get_time() + " >> " + str(context.author) + " permission denied in GUILD[" + str(context.guild) + "], CHANNEL[" + str(context.channel) + "]")