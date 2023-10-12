'''Various functions that mess with people if they're in a voice call and message a specific word'''

from discord import Message, Forbidden

from bot import bot_client
from auxiliary import log, get_time, play_audio

@bot_client.listen("on_message")
async def no_u(message: Message):
    '''If either 'die' or 'kill yourself' are messaged, disconnect user and play suicide.ogg'''

    # Disable for bots and people not in vc
    if message.author.bot or message.author.voice is None or message.author.voice.channel is None:
        return
    
    if "die" in message.content.lower() or "kill yourself" in message.content.lower():
        log(get_time() + " >> " + str(message.author) + " is being NO U'ed in GUILD[" + str(message.guild) + "], CHANNEL[" + str(message.channel) + "]")
        try:
            # Disconnect user by setting voice channel to none
            vc = message.author.voice.channel
            await message.author.edit(voice_channel = None)
        except Forbidden:
            log("ERROR HAS OCCURRED   >> Meridia couldn't disconnect " + str(message.author) + "!")
        else:
            await message.channel.send("no u", reference = message)
            await play_audio(vc, "suicide")


@bot_client.listen("on_message")
async def rise(message: Message):
    '''If 'rise' is messaged, raise user by one voice call and play rise.ogg'''

    # Disable for bots and people not in vc
    if message.author.bot or message.author.voice is None or message.author.voice.channel is None:
        return
    
    if "rise" in message.content.lower():
        log(get_time() + " >> Tarnished " + str(message.author) + " is being risen in GUILD[" + str(message.guild) + "], CHANNEL[" + str(message.channel) + "]")
        try:
            # test if user is in the top voice channel
            vc_list = message.author.guild.voice_channels
            current_index = vc_list.index(message.author.voice.channel)
            if current_index == 0:
                log("ERROR HAS OCCURRED   >> " + str(message.author) + " is already in the top channel!")
                return
            
            # get vc right above it and set user's vc to that
            await message.author.edit(voice_channel = vc_list[current_index - 1])
        except Forbidden:
            log("ERROR HAS OCCURRED   >> Meridia couldn't move " + str(message.author) + "!")
        else:
            await message.channel.send("OHHhh, RISE NOW, YE TARNISHED. Ye *DEAD*, who yet *LIVE*.\nThe call of long-lost grace *speaks to us all*.", reference = message)
            await play_audio(vc_list[current_index], "rise")

@bot_client.listen("on_message")
async def sandstorm(message: Message):
    '''If 'sandstorm' is messaged, play sandstorm.ogg'''

    # Disable for bots and people not in vc
    if message.author.bot or message.author.voice is None or message.author.voice.channel is None:
        return
    
    if "sandstorm" in message.content.lower():
        log(get_time() + " >> " + str(message.author) + " is being surprise daruded in GUILD[" + str(message.guild) + "], CHANNEL[" + str(message.channel) + "]")

        await play_audio(message.author.voice.channel, "sandstorm")