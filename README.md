# RemindMe Bot
A discord.py bot for making and sending reminders, with "classes" assigned to them, managed in a sqlite3 database

## Current features
- Add new reminders and show currently created ones
- Add new classes

## Implementation
- Built on discord.py for running the bot and sqlite3 for managing the database
- Utilizes discord's slash commands (Application Commands scope required)

## How to run
1. Clone the repository
2. Install dependencies (to-do: provide a requirements file)
3. (Optional) Install sqlite3 and pass it to PATH for managing the project's database outside of the bot in your CLI (or for troubleshooting)
4. Change the config.env.x to .env **(bot has a set path for env file so the naming is important)**
5. Run the bot

## Planned features
- Show currently created classes
- Send notifications to a set channel or in dms (tbd)
- Store data on how many notifications has been sent

## Contact
If you have any questions about current or planned features, feel free to:
- Start a discussion in the [Discussions](https://github.com/jroznowski/remindme-bot/discussions) tab.
- Open an issue in the [Issues](https://github.com/jroznowski/remindme-bot/issues) tab.
