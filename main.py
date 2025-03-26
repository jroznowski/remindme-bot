from discord import *
from discord.ui import Button, View
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import asyncio
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
if guild_id is None:
    raise ValueError("Something wrong with guild id!")
if guild_id is not None:
    print("guild id is " + guild_id)

cursor.execute("""CREATE TABLE IF NOT EXISTS Class(
               ClassId INTEGER PRIMARY KEY, 
               ClassName text NOT NULL UNIQUE)""")

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

@bot.tree.command(name="add_class",description="Add a new class to use for future reminders")
@app_commands.describe(class_name="Name of the class to add")
async def add_class(interaction: Interaction, class_name: str):
    cursor.execute("""INSERT INTO Class(ClassName)
                   VALUES(?)
                   ON CONFLICT DO NOTHING""", (class_name,))
    dbconn.commit()
    if cursor.rowcount > 0:
         await interaction.response.send_message(class_name + " has been successfully commited to the database.")
    else:
        await interaction.response.send_message("Class already exists in the table.")

@bot.tree.command(name="add_reminder",description="Add a new reminder based on your specifications")
@app_commands.describe(reminder_name = "Name of new reminder", expiry = "Date of the reminder in YYYY-MM-DD HH:MM:SS format", class_name="Name of the class for which the reminder is set")
async def add_reminder(interaction: Interaction, reminder_name: str, expiry: str, class_name: str):
    try:
        date = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        await interaction.response.send_message("Wrong date format! Provide date in YYYY-MM-DD HH:MM:SS")
        raise ValueError("Invalid format.")

    await interaction.response.send_message(date)
   


@bot.event
async def on_ready():
    guild = Object(id = int(guild_id))
    await bot.tree.sync(guild = guild)
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(token)