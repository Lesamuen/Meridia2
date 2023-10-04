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
- Get ffmpeg into PATH
- Put bot token in settings/bottoken.txt file
- Fill out Discord user IDs in settings/perms.json

## Current Capabilities
- Touching the Beacon (Audio support, touches tracking)