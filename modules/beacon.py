'''Contains event listeners and event logic related to touching the beacon'''

from typing import List
from datetime import datetime, timedelta

from discord import Message, TextChannel, Member, RawReactionActionEvent, ApplicationContext

from bot import bot_client, database_connector
from auxiliary import playAudio, log, get_time, d, ordinal
from dbmodels import User

quest_dialogue = [
    "*A new supplicant approaches. Listen, hear me and obey.*",
    "*A foul darkness has seeped into my temple. A darkness that you will destroy.*",
    "*You have found my beacon. But it is not time for rejoicing. The defiler continues to profane my temple.*"
    "*Return my Beacon to Mount Kilkreath. And I will make you the instrument of my cleansing light.*",
    "*Look at my temple, lying in ruins. So much for the constancy of mortals, their crafts and their hearts.*",
    "*If they love me not, how can my love reach them? Restore to me my beacon, that I might guide you toward your destiny.*",
    "*It is time for my splendor to return to Skyrim. But the token of my truth lies buried in the ruins of my once great temple, now tainted by a profane darkness skittering within.*",
    "*The Necromancer Malkoran defiles my shrine with vile corruptions, trapping lost souls left in the wake of this war to do his bidding.*",
    "*Worse still, he uses the power stored within my own token to fuel his foul deeds.*",
    "*I have brought you here, mortal, to be my champion. You will enter my temple, retrieve my artifact, and destroy the defiler.*",
    "*Mortals call it Dawnbreaker, for it was forged in a holy light that breaks upon my foes, burning away corruption and false life.*",
    "*You will enter my shrine, destroy Malkoran, and retrieve this mighty blade.*",
    "*A single candle can banish the darkness of the entire Void. If not you, then someone else.*",
    "*My beacon is sure to attract a worthy soul. But if you are wise, you will heed my bidding.*",
    "*Guide my light through the temple to open the inner sanctum and destroy the defiler.*",
    "*I have commanded it! Go now, the artifact must be reclaimed and Malkoran destroyed.*",
    "*Malkoran has forced the doors shut. But this is my temple, and it responds to my decree.*",
    "*I will send down a ray of light. Guide this light through my temple and its doors will open.*",
    "```Objective: Guide Meridia's Light through the temple\nTarget: Kilkreath Temple, below the Statue to Meridia```",
    "You toss spell after strike at Malkoran, and consume many of your cheese wheels, and yet he still stays standing..."
]

def beacon_roll() -> List[int]:
    '''
    Rolls 3d20 for the beacon touch

    ### Returns
    results of 3 d20s, sorted from highest to lowest
    '''

    results = [d(1, 20), d(1, 20), d(1, 20)]
    results.sort(reverse = True)
    return results

async def beacon_touch(channel: TextChannel, toucher: Member) -> None:
    '''
    Handles all beacon touching logic (since multiple events trigger the same code)

    If user has either lost the beacon (progress -1) or obtained the dawnbreaker (progress 20), then beacon cannot be touched; special message will play instead.
    Once every day, can try to find the beacon again; rolls a single d20, and on a 20, progress becomes 0 again.

    On every beacon touch, 3d20 will be rolled. Given two 20s, quest progress will be increased by 1, and new dialogue will be given.
    Progress locked at 19, until three 20s are rolled, at which progress is skipped to 20.
    Every two 20s rolled gives +1 electrum. Obtaining the dawnbreaker gives +50 electrum.

    If all numbers are a 1 digit number, then unable to touch beacon for 10 minutes. If three 1s, then unable to touch beacon until found again.

    Responds to generic touches with variants of "A NEW HAND TOUCHES THE BEACON".

    If author was is in a voice channel, will also join the same voice channel and play the quote.

    ### Parameters
    channel: TextChannel
        The text channel where the beacon was touched
    
    toucher: Member
        The Discord user who touched the beacon
    '''

    if not channel.can_send(Message):
        log(get_time() + " >> " + str(toucher) + " tried to touch the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]\nERROR HAS OCCURRED   >> Meridia's influence does not reach there!")
        return

    session = database_connector()

    user = User.find_user(session, toucher.id)

    # Dawnbreaker has already been found
    if user.dawnbreaker_progess == 20:
        log(get_time() + " >> Dawnbreaker-bearer " + str(toucher) + " tried to touch the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

        # Coin flip between 2 dialogue possibilities
        if d(1, 2) == 1:
            await channel.send("*" + toucher.mention + ", may the light of certitude guide your efforts.*", delete_after = 60)
        else:
            await channel.send("*" + toucher.mention + ", as you carry Dawnbreaker, so will my light touch the world.*", delete_after = 60)

        session.close()
        return

    # Reset cooldown if any, if it has passed
    if user.beacon_cd is not None and datetime.utcnow() > user.beacon_cd:
        user.reset_cd(session)

    # When beacon has already been lost and user tries to touch the beacon
    if user.dawnbreaker_progess == -1:
        if user.beacon_cd is not None:
            # user has a cooldown active
            log(get_time() + " >> " + str(toucher) + " was too tired to find the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

            await channel.send("Unfortunately, " + toucher.mention + ", you are much too tired to continue your search for the beacon today.", delete_after = 60)

        else:
            # attempt to find the beacon; cooldown 1 day upon fail
            log(get_time() + " >> " + str(toucher) + " tried to find the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

            message = toucher.mention + ", you set out to search for the beacon once again today.\n`| "
            beacon_search = d(1, 20)
            message += str(beacon_search) + " |`"

            log("                     >> Result: " + str(beacon_search))

            if beacon_search == 20:
                # successfully found the beacon again; reset progress
                user.dawnbreaker(session, 0)

                log("                     >> " + str(toucher) + " Dawnbreaker progress reset to 0")
                message += "\nAmazingly, you finally find the :touchesthebeacon:, right in the last place you look: your back pocket! Don't misplace it next time!"

            else:
                # failed to find the beacon
                message += "\nDespite all your efforts, wardrobes opened, chests unlocked, and display cases upturned, you still haven't found the beacon!"
                user.set_cd(session, timedelta(days = 1))
                log("                     >> " + str(toucher) + " cooldown set to 1 day")

            await channel.send(message)

        session.close()
        return
    
    if user.beacon_cd is not None:
        # cooldown active for pissing off meridia
        log(get_time() + " >> " + str(toucher) + " tried to touch the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

        await channel.send("*Meridia's voice does not grace you. It seems that she is still a little peeved by your mistreatment of the beacon.*", delete_after = 60)

        session.close()
        return


    log(get_time() + " >> " + str(toucher) + " has touched the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

    user.touch_beacon(session)
    beacon_result = beacon_roll()

    log("                        Touch #" + str(user.beacon_touches) + ", Rolls: " + str(beacon_result[0]) + "|" + str(beacon_result[1]) + "|" + str(beacon_result[2]))

    # Decide the message used for touching the beacon
    if user.beacon_touches == 1:
        message = "**A NEW HAND TOUCHES THE BEACON!**"
    elif user.beacon_touches == 2:
        message = "**A NEW HAND TOUCHES THE BEACON.**"
    elif user.beacon_touches == 3:
        message = "**" + toucher.mention + " TOUCHES THE BEACON.**"
    elif user.beacon_touches == 4:
        message = "**" + toucher.mention + " TOUCHES THE BEACON AGAIN.**"
    elif user.beacon_touches == 5:
        message = "**" + toucher.mention + " TOUCHES THE BEACON. AGAIN.**"
    elif user.beacon_touches == 6:
        message = "**" + toucher.mention + " TOUCHES THE BEACON. AGAIN...**"
    else:
        message = "**" + toucher.mention + " TOUCHES THE BEACON. AGAIN. FOR THE " + ordinal(user.beacon_touches) + " TIME.**"
    message += "\n`| " + str(beacon_result[0]) + " | " + str(beacon_result[1]) + " | " + str(beacon_result[2]) + " |`"
    await channel.send(message, delete_after = 60)

    # If connected to a voice channel, play meridia.ogg
    if toucher.voice:
        await playAudio(toucher.voice.channel, "meridia")
    
    if beacon_result[0] == 1:
        # Sorted descending; if first is 1, then all are 1
        # Lose the beacon; progress -1
        await channel.send("**THAT IS ENOUGH, " + toucher.mention + ". I AM--WAIT. WHERE DID YOU PUT THE BEACON?**\nYou search your inventory; it was right there just a moment ago!\n***HOW DID YOU EVEN MANAGE TO LOSE MY BEACON?!*** **FIND IT, AND I MAY FORGIVE YOU YET.**")
        user.dawnbreaker(session, -1)
        log("                     >> " + str(toucher) + " Dawnbreaker progress set to -1")

        session.close()
        return

    if beacon_result[0] < 10:
        # Sorted descending; if first is 1 digit, then all are 1 digit
        # 10 min cooldown
        await channel.send("**THAT IS ENOUGH, " + toucher.mention + ". I AM DISHEARTENED BY YOUR MISTREATMENT OF MY BEACON.**")
        user.set_cd(session, timedelta(minutes = 10))
        log("                     >> " + str(toucher) + " cooldown set to 10 minutes")

        session.close()
        return
        
    if beacon_result[1] == 20:
        # Sorted descending; first num guaranteed to be 20
        if beacon_result[2] == 20:
            # PULL THE DAWNBREAKER
            user.dawnbreaker(session, 20)
            log("                     >> " + str(toucher) + " Dawnbreaker progress set to 20")
            user.add_electrum(session, 50)
            log("                     >> 50 electrum imbursed to " + str(toucher))

            await channel.send(toucher.mention + "\n*Malkoran is vanquished. Skyrim's dead shall remain at rest. This is as it should be. This is because of you. A new day is dawning. And you shall be its herald. Take the mighty Dawnbreaker and with it purge corruption from the dark corners of the world. Wield it in my name, that my influence may grow.*\n__+50 Electrum__")
            session.close()
            return

        # Increase Dawnbreaker progress
        if user.dawnbreaker_progess < 19:
            user.dawnbreaker(session, user.dawnbreaker_progess + 1)
            log("                     >> " + str(toucher) + " Dawnbreaker progress set to " + str(user.dawnbreaker_progess))
        else:
            log("                     >> " + str(toucher) + " Dawnbreaker progress is already max at 19")
        user.add_electrum(session, 1)
        log("                     >> 1 electrum imbursed to " + str(toucher))
        await channel.send(toucher.mention + "\n" + quest_dialogue[user.dawnbreaker_progess] + "\n__+1 Electrum__")

    session.close()

@bot_client.listen("on_message")
async def beacon_touch_message(message: Message):
    '''
    Detects when a beacon is touched from a user message.
    '''

    if message.author.bot:
        return
    
    if ":touchesthebeacon:" in message.content:
        await beacon_touch(message.channel, message.author)

@bot_client.listen("on_raw_reaction_add")
async def beacon_touch_reaction(payload: RawReactionActionEvent):
    '''
    Detects when a beacon is touched from a user reaction.
    '''

    if payload.member and payload.member.bot:
        return
    
    if payload.emoji.name == "touchesthebeacon":
        await beacon_touch(bot_client.get_channel(payload.channel_id), payload.member)

@bot_client.slash_command(name = "touchthebeacon", description = "Touch Meridia's Beacon", guild_only = True)
async def beacon_touch_command(context: ApplicationContext):
    '''
    Adds the command /touchthebeacon
    '''

    await context.respond("You touch the beacon.", delete_after = 60)
    await beacon_touch(context.channel, context.author)