from time import strptime
import discord
from discord.ext import commands
import os
import asyncio
import re
from datetime import datetime, timedelta
from message_cryptography import Cryptography
from mongoDB import mongo_ATA

# ----- /// Connections /// -----
TOKEN = os.getenv("ATA_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='alarm ', intents=intents)

# ----- /// /// /// -----
# ----- /// Bot Commands /// -----
# ----- /// /// /// -----

# ----- /// create user /// ----- 
@bot.command(name="register")
async def register(ctx, gmt : str) -> None : 
    result = mongo_ATA.create_user(str(ctx.author.id), gmt)
    
    if result is None :
        await ctx.send("User sucefully created!")

    elif result == "err1" : 
        await ctx.send("User already exists")

    elif result == "err2" : 
        await ctx.send("Incorrect GMT format use : ( GMT(+|-)X )")

# ----- /// Delete user /// -----
@bot.command(name="delete_user")
async def delete_user(ctx) : 

    result = mongo_ATA.delete_user(ctx.author.id)

    if result == "deleted" : 
        await ctx.send("User sucefully deleted")

    elif result == "err3" : 
        await ctx.send("User do not exists")

# ----- /// now /// -----
@bot.command(name="now")
async def now(ctx) : 
    await ctx.send(mongo_ATA.now_GMT(ctx.author.id))

# ----- /// to /// -----
@bot.command(name="to")
async def alarm(ctx, *, time_message):
    # ----- /// PATTERNS /// ------
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    pattern2 = re.compile(r"^\d{2}:\d{2}")
    pattern3 = re.compile(r"^\d{2}")

    # ----- /// STRING MODIFICATION -----
    # Separates time from "Message" using (;) as split
    if ';' in time_message:
        time, message = time_message.split(';', 1)
    else:
        time = time_message
        message = ""

    # Remove blank spaces from the zeros
    time = time.strip()
    message = message.strip()
    time = time.replace(" ", ":")

    # ----- /// PATTERN 1 00:00:00 /// -----
    if pattern.match(time):
        h, m, s = map(int, time.split(':'))
        total_seconds = h * 3600 + m * 60 + s

        now = mongo_ATA.now_GMT(ctx.author.id)
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%d/%m/%Y %H:%M:%S")

        await ctx.send(f'Alarm set to : ({formatted_future_time}).')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)
        await asyncio.sleep(total_seconds)

        f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M")
        if message == "":
            await ctx.author.send("You have set an alarm for now.")
        else:
            await ctx.author.send(f"You have set an alarm for now | {message}")

        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)

    # ----- /// PATTERN 2 00:00 /// -----
    elif pattern2.match(time):
        m, s = map(int, time.split(':'))
        total_seconds = m * 60 + s

        now = mongo_ATA.now_GMT(ctx.author.id)
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%d/%m/%Y %H:%M:%S")

        await ctx.send(f'Alarm set to : ({formatted_future_time}).')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)
        await asyncio.sleep(total_seconds)

        f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M")
        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)

        if message == "":
            await ctx.author.send("You have set an alarm for now.")
        else:
            await ctx.author.send(f"You have set an alarm for now | {message}")

    # ----- /// PATTERN 3 00 // -----
    elif pattern3.match(time):
        time = int(time)
        now = mongo_ATA.now_GMT(ctx.author.id)

        future_time = now + timedelta(seconds=time)
        formatted_future_time = future_time.strftime("%d/%m/%Y %H:%M:%S")

        await ctx.send(f'Alarm set to : ({formatted_future_time}).')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)
        await asyncio.sleep(time)

        f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S")
        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)

        if message == "":
            await ctx.author.send("You have set an alarm for now.")
        else:
            await ctx.author.send(f"You have set an alarm for now | {message}")

# ----- /// set /// -----
@bot.command(name="set")
async def set(ctx, *, time_message):
    has_message = False
    message = ""

    try:
        time_message, message = time_message.split(";", 1)
        time_message = time_message.strip()
        has_message = True

    except Exception as e:
        pass

    now = mongo_ATA.now_GMT(ctx.author.id) 
    hour_input = datetime.strptime(time_message, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    formatted_hour = hour_input.strftime("%d/%m/%Y %H:%M:%S")
    time_diff = (hour_input - now).total_seconds()

    if time_diff <= 0:
        await ctx.send("You cannot set an alarm for the past.")
        return

    await ctx.send(f"Alarm set for : ({formatted_hour})")
    Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_hour, message)
    await asyncio.sleep(time_diff)

    if has_message:
        await ctx.author.send(f"You have set an alarm for now | {message}")
    else:
        await ctx.author.send("You have set an alarm for now.")

    f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S")
    mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)


# ----- /// setus /// -----
@bot.command(name="setus")
async def setus(ctx, *, time_message):
    has_message = False
    message = ""

    try:
        time_message, message = time_message.split(";", 1)
        time_message = time_message.strip()
        has_message = True
    except Exception as e:
        pass

    now = mongo_ATA.now_GMT(ctx.author.id)
    pattern = r"^(1[0-2]|0?[1-9]):([0-5][0-9]):([0-5][0-9])\s?(AM|PM)$"
    match = re.match(pattern, time_message, re.IGNORECASE)

    if not match:
        await ctx.send("Incorrect format, use HH:MM:SS AM/PM")
        return

    hour_input = datetime.strptime(time_message, "%I:%M:%S %p").replace(
        year=now.year, month=now.month, day=now.day
    )
    formatted_hour = hour_input.strftime("%m/%d/%Y %I:%M %p")
    await ctx.send(f"Alarm set for : ({formatted_hour})")
    Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_hour, message)

    time_diff = (hour_input - now).total_seconds()
    await asyncio.sleep(time_diff)

    if has_message:
        await ctx.author.send(f"You have set an alarm for now | {message}")
    else:
        await ctx.author.send("You have set an alarm for now.")

    f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S")
    mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)


# ----- /// active alarms /// -----
@bot.command(name="active")
async def active_alarms(ctx) : 
    alarms = mongo_ATA.active_alarms(ctx.author.id)

    alarms = [document for document in alarms]    

    for alarm in alarms : 
        DtS = alarm.get("Date_to_Send")
        CaT = alarm.get("Created_At")

        await ctx.author.send(f"Created at : {CaT} | Date to Send : {DtS}")


# ----- /// clear messages /// -----
@bot.command(name="clear_messages")
@commands.has_permissions(manage_messages=True)  # Requer permissão para gerenciar mensagens
@commands.has_permissions(administrator=True)
async def clear(ctx, limit):

    try : 
        max_limit = int(limit)

    except Exception as e:
        await ctx.send("limit must be integer value greater than 0")
    
    if max_limit <= 0:
        await ctx.send("Channel must have at least 1 mesage")
        return
    
    # Exclui mensagens no canal
    deleted = await ctx.channel.purge(limit=max_limit)
    await ctx.send(f'{len(deleted)} mensagens foram excluídas.', delete_after=5)


# ----- /// Contar menssagens /// -----
@bot.command(name="count_messages")
@commands.has_permissions(manage_messages=True)  # Requer permissão para gerenciar mensagens
async def count_messages(ctx):
    total_messages = 0
    async for message in ctx.channel.history(limit=None):  # Itera sobre todas as mensagens
        total_messages += 1
    
    await ctx.send(f'O número total de mensagens no canal é: {total_messages}')


# ----- /// tutorial /// -----
@bot.command(name='tutorial')
async def tutorial(ctx):
    # Cria o embed com um título e uma cor destacada
    embed = discord.Embed(
        title="Alan the alarm",
        description="Learn how to use Alan the Alarm.\n",
        color=discord.Color.red()
        #https://ibb.co/GCV1j2V 
    )

    embed.set_image(url="https://i.ibb.co/HGrMQzr/a388155e-aaf5-43d4-bb8e-297b70cdad89.jpg")

    embed.add_field(name="📚 How to use 📚", value="Commands an standards", inline=False)
    embed.add_field(name="\n⚙️ How it works️ ⚙️", value="A brief description of how it works", inline=False)
    embed.set_footer(text="\nUse the reactions to interact.")
    embed.add_field(name="🏠 Home 🏠", value="Return to Home (this page)", inline=False)

    message = await ctx.send(embed=embed)
    
    await message.add_reaction("🏠")
    await message.add_reaction("📚")
    await message.add_reaction("⚙️")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:  
        return
    
    message = reaction.message
    embed = message.embeds[0]  

    if reaction.emoji == "📚" :
        
        embed.clear_fields() 

        embed = discord.Embed(
            title="Commands",
            description="List and use of all commands",
            color=discord.Color.green()
    )
        embed.add_field(name="`; message`", value="`; message` is not a command, but a postfix. Every alarm command can handle `; message`.\nYou can send any message of any length in the `; message` field.", inline=False)
        embed.add_field(name="`Set`", value="The `set` command schedules an alarm for a specific future time. If you need an alarm for 15:45:25, just write it.\nUsage: `alarm set (24)HH:MM:SS ; message`", inline=False)
        embed.add_field(name="`Setus`", value="Refers to USA time format (12-hour clock).\nUsage: `alarm setus (12)HH:MM:SS PM/AM ; message`", inline=False)
        embed.add_field(name="`to`", value="Acts like a countdown timer. If you need an alarm 30 minutes from now,\nuse `alarm to 30:00`.\nHours : `alarm to HH:MM:SS ; message`\nMinutes : `alarm to MM:SS ; message`\nSeconds : `alarm to SS ; message`", inline=False)
        embed.add_field(name="`active`", value="Displays all your active alarms.\nUsage: `alarm active`", inline=False)
        embed.add_field(name="`count_messages`", value="Counts all the messages in the current chat.\nUsage: `alarm count_messages`", inline=False)
        embed.add_field(name="`clear_messages`", value="`Admins only`\nDeletes a specified number of messages from the chat.\nUsage: `alarm clear_messages (number)`", inline=False)
        await message.edit(embed=embed)

    elif reaction.emoji == "⚙️" :

        embed.clear_fields()

        embed = discord.Embed(
            title="How it works",
            description="",
            color=discord.Color.purple()
        ) 

        embed.add_field(name="Data and Security", value="Although the bot doesn't handle sensitive data, we rely on strong security measures. All messages are stored with encryption.", inline=False)
        embed.add_field(name="How was ATA made?", value="ATA was built using Python, MongoDB, and discord.py.", inline=False)
        embed.add_field(name="Why?", value="ATA is a utility bot designed to help solve everyday problems.", inline=False)
        embed.add_field(name="Creators", value="Felipe Palermo", inline=False)
        await message.edit(embed=embed)

    elif reaction.emoji == "🏠" : 

        embed.clear_fields()

        embed = discord.Embed(
            title="Alan the alarm",
            description="Learn how to use Alan the Alarm.\n",
            color=discord.Color.red()
        )        

        embed.set_image(url="https://i.ibb.co/HGrMQzr/a388155e-aaf5-43d4-bb8e-297b70cdad89.jpg")

        embed.add_field(name="📚 How to use 📚", value="Commands an standards", inline=False)
        embed.add_field(name="\n⚙️ How it works️ ⚙️", value="A brief description of how it works", inline=False)
        embed.set_footer(text="\nUse the reactions to interact.")

        message = await message.edit(embed=embed)


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the required permissions to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid number of messages to clear.")
    else:
        await ctx.send("An error occurred while executing the command.")


# ----- /// Verificar envio pendente /// ----- 
@bot.event
async def repeat_task():
    await bot.wait_until_ready()  # Aguarda o bot estar pronto
    while not bot.is_closed():
        alarms = mongo_ATA.active_anonymous_alarms()
        for alarm in alarms : 
            pass  

# TODO : Verificar arquivos que nao foram entregues
# durante o tempo limite 


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

if __name__ == "__main__":
    bot.run(TOKEN)