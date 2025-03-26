from discord import *
from discord.ui import Button, View
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv(dotenv_path= ".env")

token = os.getenv('BOT_TOKEN')
dbconn = sqlite3.connect(os.getenv('DATABASE_NAME'))
cursor = dbconn.cursor()
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv('BOT_PREFIX','!'), intents = intents)
guild_id = os.getenv('GUILD_ID')

cursor.execute("""CREATE TABLE IF NOT EXISTS Class(
               ClassId INTEGER PRIMARY KEY, 
               ClassName text NOT NULL)""")

dbconn.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS Reminder(
               ReminderId INTEGER PRIMARY KEY, 
               ReminderName text NOT NULL,
               Expiry datetime NOT NULL,
               ClassId INTEGER,
               FOREIGN KEY (ClassId) REFERENCES Class(ClassId))""")

dbconn.commit()

@bot.tree.command(name="show_reminders",description="Show currently created reminders")
async def show_reminders(interaction: Interaction):
    remindem = Embed(title="All reminders", description="A set of currently created reminders")
    cursor.execute("SELECT ReminderId,ReminderName,Expiry,Class.ClassName FROM Reminder INNER JOIN Class ON Reminder.ClassId = Class.ClassId")
    data = cursor.fetchall()
    data_format = []
    for row in data:
        reminder_id = row[0]
        reminder_name = row[1]
        expiry = row[2]
        class_name = row[3]

        reminder = {
            "id": reminder_id,
            "name": reminder_name,
            "expiry": expiry,
            "class_name": class_name
        }

        data_format.append(reminder)

    for reminder in data_format:
        remindem.add_field(name=f"{reminder['name']}",value=f"Associated class: {reminder['class_name']}, Expiry date: {reminder['expiry']}")
    await interaction.response.send_message(embed = remindem)

@bot.event
async def on_ready():
    guild = Object(id = guild_id)
    await bot.tree.sync(guild = guild)
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(token)