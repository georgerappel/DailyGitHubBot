## Daily GitHub Bot
for Telegram.

- Copy the file `config.inc.example` to `config.ini` and replace the bot token with your token.
- Install the requirements: `pip3 install -r requirements.txt`
  - If you get an error for the telegram package, try running the command above with sudo.
- Run the bot: `python3 bot.py`


### Todo

- [ ] Config to disable notifications if there are no commits that day, instead of sending "No commits today"
- [ ] Remove chat from the database if there's no activity for the past two weeks or so
