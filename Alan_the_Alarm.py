import discord
from discord.ext import commands
import os 
import ssl
import certifi
import aiohttp
import asyncio
import re
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient

from mongoDB import mongo_ATA

TOKEN = os.getenv("TOKEN")
Uri = os.getenv("MongoDB_URI")

Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Alarm"]

# Criar contexto SSL personalizado
ssl_context = ssl.create_default_context(cafile=certifi.where())

class CustomConnector(aiohttp.TCPConnector):
    def __init__(self, *args, **kwargs):
        kwargs['ssl'] = ssl_context
        super().__init__(*args, **kwargs)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='al', intents=intents)

@bot.command(name="arm")
async def alarm(ctx, *, time_message):


# ----- /// PATTERNS /// ------ 
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    pattern2 = re.compile(r"^\d{2}:\d{2}")
    pattern3 = re.compile(r"^\d{2}")

# ----- /// STRING MODIFICATION -----
# ----- /// separes time from "Message" using (;) as split ----- ///

    if ':' in time_message:
        time, message = time_message.split(':', 1)
    else:
        time = time_message
        message = "None"

    # Remove blank sapces from the zeros 
    time = time.strip()
    message = message.strip()
    time = time.replace(" ", ":")

# ----- /// PATTERN 1 00 00 00 /// -----

    if pattern.match(time):
        h, m, s = map(int, time.split(':'))
        total_seconds = h * 3600 + m * 60 + s

        now = datetime.now()
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%d/%m %H:%M:%S")

        await ctx.send(f'Alarm set to : ({formatted_future_time}). Message: {message}')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)

        await asyncio.sleep(total_seconds)

        f_time = now.strftime("%d/%m %H:%M:%S")
        await ctx.author.send(f"Mensagem : {message}")
        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)


# ----- /// PATTERN 2 00 00 /// -----

    elif pattern2.match(time):
        m, s = map(int, time.split(':'))
        total_seconds = m * 60 + s

        now = datetime.now()
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%d/%m %H:%M:%S")


        await ctx.send(f'Alarm set to : ({formatted_future_time}). Message: {message}')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)


        await asyncio.sleep(total_seconds)

        f_time = now.strftime("%d/%m %H:%M")
        await ctx.author.send(f"Mensagem : {message}")
        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)



# ----- /// PATTERN 3 00 // -----

    elif pattern3.match(time):

        time = int(time)
        now = datetime.now()

        future_time = now + timedelta(seconds=time)
        formatted_future_time = future_time.strftime("%d/%m %H:%M:%S")

        await ctx.send(f'Alarm set to : ({formatted_future_time}). Message: {message}')
        Document_ID = mongo_ATA.insert_timer(str(ctx.author.id), formatted_future_time, message)

        await asyncio.sleep(time)

        f_time = now.strftime("%d/%m %H:%M:S")
        await ctx.author.send(f"Mensagem : {message}")
        mongo_ATA.true_mailed(str(ctx.author.id), f_time, Document_ID)



@bot.command(name="stop")
async def stop(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.channel == channel:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send('O bot não está no mesmo canal de voz que você.')
    else:
        await ctx.send('Você não está em um canal de voz.')


@bot.event
async def send_late():
    documents = Client["Discord_Timers"].find()
    if documents > 1 :  # type: ignore
        for document in documents:
            if document["Mailed"] is False : 
                user = await bot.fetch_user(document["Discord_ID"])

                await user.send(f"LATE ALARM : It was supposed to be sent {document["Date_to_send"]}")
                await user.send(f"Message : {document["Message"]}")
                await user.send(f"Created at : {document["Created_At"]}")
                    
                Client["Discord_Timers"].delete_one({"_id" : document["_id"]})

            else : 
                pass 
    else : 
        pass 

@bot.event
async def on_ready():
    #send_late.start()  # Inicia o loop de tarefas
    print(f'Logged in as {bot.user.name}') # type: ignore

bot.run(TOKEN) # type: ignore

#TODO Implementar menssagem nos alarmes 
#TODO Implementar criacao e exclusao automatica no banco de dados
#TODO Implementar menssagem direta em todos os alarmes 
