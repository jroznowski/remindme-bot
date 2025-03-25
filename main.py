import discord
from discord.ui import Button, View
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

token = os.getenv('BOT_TOKEN')
dbconn = sqlite3.connect(os.getenv('DATABASE_NAME'))
curson = dbconn.cursor()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv('BOT_PREFIX','!'), intents = intents)

guild_id = os.getenv('GUILD_ID')

@bot.event
async def on_ready():
    guild = discord.Object(id = guild_id)
    await bot.tree.sync(guild = guild)
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(token)