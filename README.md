## History
This is the code for a joke discord bot named Meridia, written in Python3.11 with Pycord.

It started with one single functionality, based on the famous "Meridia's Beacon" from the game The Elder Scrolls V: Skyrim.  
Everytime someone reacted with or entered a message with the :touchesthebeacon: emote, the bot would join the user's voice call and call out "A NEW HAND TOUCHES THE BEACON".

From then on, many, many other joke features have been requested and added, to the point that now, the bot needs a version control system, a database, and a full code rework.
Hence, Meridia 2.

Note: The code for Meridia 1 will not be made publicly available, because it contains too much private information, such as bot token, User IDs, Guild IDs, and Role IDs.

## Current Python Dependencies
- py-cord[voice]
- pynacl
- SQLAlchemy

## Pre-Use Steps
- Bot is designed to be used with Windows; if you are on Linux, you need to add some code to manually load the Opus library in main.py for voice to work.
- Get ffmpeg into PATH
- Put bot token in settings/bottoken.txt file
- Fill out Discord user IDs in settings/perms.json
- Servers using this bot should add a :touchesthebeacon: emote that is a picture of Meridia's beacon.

## Current Capabilities
- User tracking (beacon-related info, electrum currency)
- Touching the Beacon (vc support, touches tracking, quest to find the Dawnbreaker, electrum rewards, special emote usage, 2 ways to do it)