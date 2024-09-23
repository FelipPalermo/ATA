import discord
from discord.ext import commands
import os
import asyncio
import re
from datetime import datetime, timedelta
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

# ----- /// Change GMT /// -----
@bot.command(name="change_gmt")
async def change_gmt(ctx,  gmt : str) -> None : 
    result = mongo_ATA.Change_GMT(ctx.author.id, gmt) 

    if result == "Updated": 
        await ctx.send("GMT successfully updated.")
    elif result == "err1": 
        await ctx.send("Invalid format. Please use ( GMT(+ | -)(0-12) ).")
    else: 
        await ctx.send("You are not registered.")

# ----- /// now /// -----
@bot.command(name="now")
async def now(ctx) : 

    await ctx.send(mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S"))

# ----- //// Now US /// -----
@bot.command(name="nowus")
async def nowus(ctx) : 
    await ctx.send(mongo_ATA.nowus_GMT(ctx.author.id).strftime("%m/%d/%Y %I:%M:%S %p"))

# ----- /// Alarms /// -----
def time_to_seconds(h=0, m=0, s=0):
    return h * 3600 + m * 60 + s

async def set_alarm(ctx, total_seconds, message, formatted_time, timer_type):
    await ctx.send(f'Alarm set to : ({formatted_time}).')
    Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_time, message, timer_type)
    await asyncio.sleep(total_seconds)

    now_str = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S")
    mongo_ATA.true_mailed(str(ctx.author.id), now_str, Document_ID)

    if message:
        await ctx.author.send(f"You have set an alarm for now | {message}")
    else:
        await ctx.author.send("You have set an alarm for now.")

@bot.command(name="to")
async def alarm(ctx, *, time_message):
    # Padrões ajustados para aceitar tanto ":" quanto " " como separadores
    pattern_hms = re.compile(r'^\d{2}[: ]\d{2}[: ]\d{2}$')
    pattern_ms = re.compile(r'^\d{2}[: ]\d{2}$')
    pattern_s = re.compile(r'^\d{2}$')

    # Dividindo a entrada entre o tempo e a mensagem
    time, message = (time_message.split(';', 1) + [""])[:2]
    time, message = time.strip(), message.strip()

    # Verificando qual padrão o tempo se encaixa
    if pattern_hms.match(time):
        # Usando re.split para dividir por ":" ou " "
        h, m, s = map(int, re.split('[: ]', time))
    elif pattern_ms.match(time):
        h, m, s = 0, *map(int, re.split('[: ]', time))
    elif pattern_s.match(time):
        h, m, s = 0, 0, int(time)
    else:
        await ctx.send("Formato inválido. Use HH:MM:SS, HH MM SS, MM:SS, MM SS, ou SS.")
        return

    total_seconds = time_to_seconds(h, m, s)
    now = mongo_ATA.now_GMT(ctx.author.id)
    future_time = now + timedelta(seconds=total_seconds)
    formatted_time = future_time.strftime("%d/%m/%Y %H:%M:%S")

    await set_alarm(ctx, total_seconds, message, formatted_time, "to")

# ----- /// set /// -----
@bot.command(name="set")
async def set(ctx, *, time_message: str):
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    time_message, message = (time_message.split(";", 1) + [""])[:2]
    time_message = time_message.strip()
    has_message = bool(message.strip())

    # Verifica o formato do horário (24 horas)
    if not pattern.match(time_message):
        await ctx.send("Invalid format, use HH:MM:SS")
        return

    # Obtém o fuso horário do usuário e cria o datetime no formato correto
    user_timezone = mongo_ATA.GMT(ctx.author.id)
    now = mongo_ATA.now_GMT(ctx.author.id)
    hour_input = datetime.strptime(time_message, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    hour_input = user_timezone.localize(hour_input) # type: ignore

    # Calcula a diferença de tempo
    time_diff = (hour_input - now).total_seconds()
    if time_diff <= 0:
        await ctx.send("You cannot set an alarm for the past.")
        return

    # Formata e confirma o alarme
    formatted_hour = hour_input.strftime("%d/%m/%Y %H:%M:%S")
    await ctx.send(f"Alarm set for: ({formatted_hour})")

    # Insere o alarme no banco de dados
    document_id = mongo_ATA.insert_timer(str(ctx.author.id), formatted_hour, message, "set")

    # Aguarda até o horário definido
    await asyncio.sleep(time_diff)

    # Envia mensagem de alarme
    alarm_message = f"You have set an alarm for now{' | ' + message if has_message else '.'}"
    await ctx.author.send(alarm_message)

    # Confirma o envio do alarme no banco de dados
    f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%d/%m/%Y %H:%M:%S")
    mongo_ATA.true_mailed(str(ctx.author.id), f_time, document_id)

# ----- /// setus /// -----
@bot.command(name="setus")
async def setus(ctx, *, time_message: str):
    now = mongo_ATA.now_GMT(ctx.author.id)

    time_message, message = (time_message.split(";", 1) + [""])[:2]
    time_message = time_message.strip()
    has_message = bool(message.strip())

    pattern = r"^(1[0-2]|0?[1-9]):([0-5][0-9]):([0-5][0-9])\s?(AM|PM)$"
    if not re.match(pattern, time_message, re.IGNORECASE):
        await ctx.send("Incorrect format, use HH:MM:SS AM/PM")
        return

    user_timezone = mongo_ATA.GMT(ctx.author.id)
    hour_input = datetime.strptime(time_message, "%I:%M:%S %p").replace(
        year=now.year, month=now.month, day=now.day
    )
    hour_input = user_timezone.localize(hour_input) # type: ignore

    formatted_hour = hour_input.strftime("%m/%d/%Y %I:%M %p")
    await ctx.send(f"Alarm set for: ({formatted_hour})")

    document_id = mongo_ATA.insert_timer(str(ctx.author.id), formatted_hour, message, "setus")

    time_diff = (hour_input - now).total_seconds()
    await asyncio.sleep(time_diff)

    alarm_message = f"You have set an alarm for now{' | ' + message if has_message else '.'}"
    await ctx.author.send(alarm_message)

    f_time = mongo_ATA.now_GMT(ctx.author.id).strftime("%m/%d/%Y %I:%M %p")
    mongo_ATA.true_mailed(str(ctx.author.id), f_time, document_id)

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
@commands.has_permissions(manage_messages=True)  
@commands.has_permissions(administrator=True)
async def clear(ctx, limit):

    try : 
        max_limit = int(limit)
    except :  # noqa: E722
        await ctx.send("limit must be integer value greater than 0")
    
    if max_limit <= 0:
        await ctx.send("Channel must have at least 1 mesage")
        return
    
    deleted = await ctx.channel.purge(limit=max_limit)
    await ctx.send(f'{len(deleted)} mensagens foram excluídas.', delete_after=5)

# ----- /// Count messages /// -----
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

    embed.add_field(name="📚 How to use 📚", value="Commands and standards", inline=False)
    embed.add_field(name="👤 Create account", value="Account commands")
    embed.add_field(name="\n⚙️ How it works️ ⚙️", value="A brief description of how it works", inline=False)
    embed.set_footer(text="\nUse the reactions to interact.")
    embed.add_field(name="🏠 Home 🏠", value="Return to Home (this page)", inline=False)

    message = await ctx.send(embed=embed)
    
    await message.add_reaction("🏠")
    await message.add_reaction("👤")
    await message.add_reaction("📚")
    await message.add_reaction("⚙️")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:  
        return
    
    message = reaction.message
    embed = message.embeds[0]  
    if reaction.emoji == "👤" : 
        embed.clear_fields() 

        embed = discord.Embed(
            title="Commands",
            description="Register and account",
            color=discord.Color.dark_purple()
    ) 

    embed.add_field(name="`register`", value="You must register yourself to use the bot.\nUsage: `alarm register ( gmt(+ | -)(0 - 12) )`")
    embed.add_field(name="", value="")
    embed.add_field(name="`delete_user`", value="Delete your user.\nUsage: `alarm delete_user`")
    embed.add_field(name="`change_gmt`", value="Change GMT associated to your account.\nUsage: `alarm change_gmt ( gmt(+ | -)(0 - 12) )`")    
    await message.edit(embed=embed)

    if reaction.emoji == "📚" :
        
        embed.clear_fields() 

        embed = discord.Embed(
            title="Commands",
            description="List and use of all commands",
            color=discord.Color.green()
    )
        embed.add_field(name="`; message`", value="`; message` is not a command, but a postfix. Every alarm command can handle `; message`.\nYou can send any message of any length in the `; message` field.", inline=False)
        embed.add_field(name="`to`", value="Acts like a countdown timer. If you need an alarm 30 minutes from now,\nuse `alarm to 30:00`.\nHours : `alarm to HH:MM:SS ; message`\nMinutes : `alarm to MM:SS ; message`\nSeconds : `alarm to SS ; message`", inline=False)
        embed.add_field(name="`Set`", value="The `set` command schedules an alarm for a specific future time. If you need an alarm for 15:45:25, just write it.\nUsage: `alarm set (24)HH:MM:SS ; message`", inline=False)
        embed.add_field(name="`Setus`", value="Refers to USA time format (12-hour clock).\nUsage: `alarm setus (12)HH:MM:SS PM/AM ; message`", inline=False)
        embed.add_field(name="`now`", value="Show current time in 24 time system.\nUsage: `alarm now`")
        embed.add_field(name="`nowus`", value="Show current time in 12 time system.\nUsage: `alarm nowus`")
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

@setus.error
async def setus_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, KeyError):
        await ctx.send("No timezone found for your user. Please configure it before using this command.")
    else:
        await ctx.send("An error occurred while executing the command.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}') # type: ignore

if __name__ == "__main__":
    bot.run(TOKEN) # type: ignore