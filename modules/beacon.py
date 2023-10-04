'''Event listeners related to touching the beacon'''

from bot import bot_client, database_connector
from auxiliary import playAudio, log, getTime
from dbmodels import User

from discord import Message, TextChannel, Member, Forbidden, RawReactionActionEvent

async def beacon_touch(channel: TextChannel, toucher: Member) -> None:
    '''
    Handles all beacon touching logic (since multiple events trigger the same code)

    Responds to original message with "A NEW HAND TOUCHES THE BEACON".

    If author was is in a voice channel, will also join the same voice channel and play the quote.

    ### Parameters
    channel: TextChannel
        The text channel where the beacon was touched
    
    toucher: Member
        The Discord user who touched the beacon
    '''

    session = database_connector()
    
    user = User.find_user(session, toucher.id)

    log(getTime() + " >> " + str(toucher) + " has touched the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

    try:
        await channel.send("**A NEW HAND TOUCHES THE BEACON.**", delete_after = 60)
    except Forbidden: 
        log("ERROR HAS OCCURRED   >> Meridia's influence cannot reach there!")
    else:
        user.touch_beacon(session)
        log("                        Touch #" + str(user.beacon_touches))

    # If connected to a voice channel, play meridia.ogg
    if toucher.voice:
        await playAudio(toucher.voice.channel, "meridia")

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