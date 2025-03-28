from discord import *
from discord.ui import Button, View
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import os
import sqlite3

load_dotenv(dotenv_path= ".env")

"""Getting appropriate data from the .env file and changing the setup hook to load cogs and sync commands"""
token = os.getenv('BOT_TOKEN')
intents = Intents.default()
intents.message_content = True

guild_id = os.getenv('GUILD_ID')
guild = Object(id=int(guild_id))
if guild_id is None:
    raise ValueError("Something wrong with guild id!")
else:
    print("guild id is " + guild_id)

class remindmeBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.db_mgmt")
        commands = await self.tree.sync(guild = guild)
        for item in commands:
            print(item)
        print(f"Logged in as {self.user}")

bot = remindmeBot(command_prefix=os.getenv('BOT_PREFIX','!'), intents = intents)
bot.tree.clear_commands(guild = None)
bot.tree.clear_commands(guild = guild)

if __name__ == "__main__":
    bot.run(token)