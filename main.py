from discord import *
from discord.ui import Button, View
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import os
import sqlite3

load_dotenv(dotenv_path= ".env")

"""Managing connecting to the database, getting appropriate data from the .env file
setup of the bot and creation of the two databases used for managing the reminders"""
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
    """View currently created reminders based on an SQL query from the bot's database, 
    passed back to the output as an formatted embed with all entries."""
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
    """Add a new class into the database, for further use in creating new reminders.
    param: class_name: str - name of the class to create"""
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
    """Add a new reminder based on user's input, then output the new reminder in a formatted embed
    param: reminder_name: str - name of the new reminder
    param: expiry: str - date of the new reminder in YYYY-MM-DD HH:MM:SS format (hard-coded for now with input verification)
    param: class_name: str - name of the class that is to be assigned to the reminder"""
    try:
        date = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        print(f"Formatted date is: {date}")
    except ValueError:
        await interaction.response.send_message("Wrong date format! Provide date in YYYY-MM-DD HH:MM:SS")
        raise ValueError("Invalid format.")

    classid_query = cursor.execute("""SELECT ClassId FROM Class WHERE ClassName = ?""",(class_name,)).fetchone()
    classid = classid_query[0] if classid_query else None
    
    """Provisional date formatting check for debugging purposes"""
    format_date = date.strftime("%Y-%m-%d %H:%M:%S")
    print(f"New date is: {format_date}")

    cursor.execute("""INSERT INTO Reminder(ReminderName,Expiry,ClassId) VALUES (?,?,?)""", (reminder_name,expiry,classid,))
    dbconn.commit()
    
    newrem = cursor.execute("""SELECT ReminderName,Expiry,Class.ClassName FROM Reminder 
                            INNER JOIN Class ON Reminder.ClassId = Class.ClassId 
                            WHERE ReminderName = ? """,(reminder_name,)).fetchone()

    newreminder = {"ReminderName" : newrem[0], "Expiry" : newrem[1], "ClassName" : newrem[2]}
    reminder_embed = Embed(title="New reminder created successfully!",description="Here are the details of the newly created reminder!")
    reminder_embed.add_field(name=f"{newreminder['ReminderName']}",value=f"Associated class: {newreminder['ClassName']}, Expiry date: {newreminder['Expiry']}")

    await interaction.response.send_message(embed=reminder_embed)  


@bot.event
async def on_ready():
    guild = Object(id = int(guild_id))
    await bot.tree.sync(guild = guild)
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(token)