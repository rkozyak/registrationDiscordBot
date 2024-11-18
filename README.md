# registrationDiscordBot
A discord bot to help Georgia Tech students keep up to date with registration

To initialize with your bot's token, cd to `registrationDiscordBot/` and run `source setup.sh YOUR_TOKEN`.
To start the bot, cd to `registrationDiscordBot/` and run `python3 src/bot.py`.
This script will store data in `/var/data/saved_requests.json`. This directory might be protected, so you may have to run in `sudo` mode.

To create a discord bot, see [Discord documentation](https://discordpy.readthedocs.io/en/stable/discord.html).