'''Event listeners related to touching the beacon'''

from bot import bot_client
from auxiliary import playAudio, log, getTime

from discord import Message, TextChannel, Member, Forbidden

async def beacon_touch(channel: TextChannel, mention: Member):
    '''
    Handles all beacon touching logic (since multiple events trigger the same code)

    Responds to original message with "A NEW HAND TOUCHES THE BEACON".
    If author was is in a voice channel, will also join the same voice channel and play the quote.
    '''

    log(getTime() + " >> " + str(mention) + " has touched the beacon in GUILD[" + str(channel.guild) + "], CHANNEL[" + str(channel) + "]")

    try:
        await channel.send("A NEW HAND TOUCHES THE BEACON.", delete_after = 60)
    except Forbidden: 
        log("ERROR >> Meridia's influence cannot reach there!")

    # If connected to a voice channel, play meridia.ogg
    if mention.voice:
        await playAudio(mention.voice.channel, "meridia")

@bot_client.listen("on_message")
async def beacon_touch_message(message: Message):
    '''
    Detects when a beacon is touched from a user message.
    '''
    if message.author.bot:
        return
    
    if ":touchesthebeacon:" in message.content:
        await beacon_touch(message.channel, message.author)