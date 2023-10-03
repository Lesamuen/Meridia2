'''Contains miscellaneous functions used in most cases'''

from discord import VoiceChannel, VoiceClient, FFmpegOpusAudio
from discord import ClientException

from datetime import datetime
from asyncio import sleep


def getTime() -> str:
    '''
    Returns the current time in extended ISO8601 format; 20 chars long
    '''

    return datetime.now().strftime("%Y-%m-%d, %H:%M:%S")


def log(out: str) -> None:
    '''
    Both prints the input string to the console and writes the input string to a dated log.

    This log is found in the logs/ folder (the logs folder has to be created first).

    ### Parameters
    out: str
        String to print to file and console
    '''

    print(out)

    with open("logs/" + datetime.now().strftime("%Y-%m-%d") + ".txt", "a") as log_file:
        log_file.write(out + "\n")


async def playAudio(vc: VoiceChannel, file: str) -> None:
    '''
    Has the bot join a voice channel, and play an audio clip from ./audio/<file>.ogg

    Bot automatically leaves after audio stops playing.

    ### Parameters
    vc: VoiceChannel
        Voice channel to join
    
    file: str
        Name of audio file to play (excluding .ogg)
    '''

    if vc is None:
        return

    log(getTime() + " >> Playing " + file + ".ogg in GUILD[" + str(vc.guild) + "], CHANNEL[" + str(vc) + "]")

    # Get bot voice client, if it exists, or create one
    voice_client: VoiceClient
    try:
        voice_client = await vc.connect()
    except ClientException:
        voice_client = vc.guild.voice_client
        if voice_client.channel is not vc:
            await voice_client.move_to(vc)

    # Detect failure to obtain voice client
    if voice_client is None:
        log("ERROR HAS OCCURRED   >> Audio commands have intersected!")
        return

    # Load audio
    try:
        audio: FFmpegOpusAudio = FFmpegOpusAudio("audio/" + file + ".ogg", codec = "copy")
    except ClientException:
        log("ERROR HAS OCCURRED   >> Audio file not found!")
        return
    
    # Play audio
    if not voice_client.is_playing():
        try:
            await voice_client.play(audio, wait_finish = True)
            if not voice_client.is_playing():
                log(getTime() + " >> Disconnecting voice client in GUILD[" + str(voice_client.guild) + "]")
                await voice_client.disconnect()
        except ClientException:
            log("ERROR HAS OCCURRED   >> Audio commands have collided!")
    else:
        voice_client.source = audio