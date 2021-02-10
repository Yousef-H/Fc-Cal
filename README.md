# Fc-Cal
Bot that tracks ical links.

way welcome to the doucmentation.

For starters if you don't have any of the databases main.py will create them, if you read main.py it explains a decent bit..

Got some help from: https://gist.github.com/meskarune/63600e64df56a607efa211b9a87fb443

Setup:
  - download/git copy the repo
  - fill out config.json
  - pip install -r requirements.txt
  - pyhton(3) main.py



Features:
- Reminders

- Messages user when new assignment is posted/added to calender. 

- setup command so users can setup their ical link

- guild setup school notifs, as well as editing the embed color, mention role id ect.


Main:

Main python file to run.

Define_stuff:

All the "backend" sql stuff is done in define stuff.

Blacklist_functions:

Blacklist functions for "backend" (sql)

Basic_commands:

Home to the bot_check event, help command, and a few staff commands + the help command

Before_after_class:

Handles before/after class times.

Cal:

All calender stuff is done in there, home to forcecheck command.

Reminder:

Reminder, reminder log, checks for when reminders expires

User_guild_setup:

User setup command, as well as guild setup command.

Last updated: 2/10/2021
