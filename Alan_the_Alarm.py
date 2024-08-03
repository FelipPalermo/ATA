
TOKEN = "MTI2ODk3Njc3MTI0NDc1MjkzNg.GAVOtN.8voHwMO6bC225sWfmiS6FHotZZUOGq0mkHVFTA"

import discord
from discord.ext import commands, tasks
import ssl
import certifi
import aiohttp
import asyncio
import re
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient


Uri = "mongodb+srv://FelipePalermo:fsrKta0YGh0MPiH4@tarrasque.zslex2g.mongodb.net/?retryWrites=true&w=majority&appName=Tarrasque"
Client = MongoClient(Uri, tlsCAFile=certifi.where())["Alan_the_Timer"]

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="arm")
async def alarm(ctx, *, time_message):
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    pattern2 = re.compile(r"^\d{2}:\d{2}")
    pattern3 = re.compile(r"^\d{2}")

    # Separar o tempo da mensagem usando ponto e vírgula como separador
    if ';' in time_message:
        time, message = time_message.split(';', 1)
    else:
        time = time_message
        message = "Alarm!"

    time = time.strip()
    message = message.strip()
    time = time.replace(" ", ":")

    if pattern.match(time):
        h, m, s = map(int, time.split(':'))
        total_seconds = h * 3600 + m * 60 + s

        now = datetime.now()
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%H:%M:%S")

        await ctx.send(f'Alarme definido para: {time}. ({formatted_future_time}). Mensagem: "{message}"')

        await asyncio.sleep(total_seconds)

        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await ctx.author.send(message)
            
            #TODO
            # voice_client = await channel.connect()
            # voice_client.play(discord.FFmpegPCMAudio('Alarm_Sound.mp3'), after=lambda e: print('done', e))

            await asyncio.sleep(10)
            # TODO await voice_client.disconnect()
        else:
            f_time = now.strftime("%d/%m/%Y  |  %H:%M")
            await ctx.author.send(f"You set an alarm for this moment. The alarm has been created {f_time}. Mensagem: {message}")

    elif pattern2.match(time):
        m, s = map(int, time.split(':'))
        total_seconds = m * 60 + s

        now = datetime.now()
        future_time = now + timedelta(seconds=total_seconds)
        formatted_future_time = future_time.strftime("%H:%M:%S")

        await ctx.send(f'Alarme definido para: {time}. ({formatted_future_time}). Mensagem: "{message}"')

        await asyncio.sleep(total_seconds)

        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await ctx.author.send(message)
            
            #TODO
            # voice_client = await channel.connect()
            # voice_client.play(discord.FFmpegPCMAudio('Alarm_Sound.mp3'), after=lambda e: print('done', e))

            await asyncio.sleep(10)
            # TODO await voice_client.disconnect()
        else:
            f_time = now.strftime("%d/%m/%Y  |  %H:%M")
            await ctx.author.send(f"You set an alarm for this moment. The alarm has been created {f_time}. Mensagem: {message}")

    elif pattern3.match(time):
        time = int(time)
        now = datetime.now()
        future_time = now + timedelta(seconds=time)
        formatted_future_time = future_time.strftime("%H:%M:%S")

        await ctx.send(f'Alarme definido para: {time} seconds. ({formatted_future_time}). Mensagem: "{message}"')

        await asyncio.sleep(time)

        if ctx.author.voice and ctx.author.voice.channel:
            await ctx.author.send(message)
            channel = ctx.author.voice.channel

            #TODO
            # voice_client = await channel.connect()
            # voice_client.play(discord.FFmpegPCMAudio('Alarm_Sound.mp3'), after=lambda e: print('done', e))

            await asyncio.sleep(10)
            # TODO await voice_client.disconnect()
        else:
            f_time = now.strftime("%d/%m/%Y  |  %H:%M")
            await ctx.author.send(f"You set an alarm for this moment. The alarm has been created {f_time}. Mensagem: {message}")

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

    if documents > 1 : 
        for document in documents:
            if document["Status"] == False : 
                user = await bot.fetch_user(document["Discord_ID"])

                await user.send(f"LATE ALARM : It was supposed to be sent {document["Date_to_send"]}")
                await user.send(f"Message : {document["Message"]}")
                await user.send(f"Created at : {document["Created_At"]}")
                    
                Client["Discord_Timers"].delete_one({"_id" : document["_id"]})

            else : pass 
    else : pass 


@bot.event
async def on_ready():
    send_late.start()  # Inicia o loop de tarefas
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)

#TODO Implementar menssagem nos alarmes 
#TODO Implementar criacao e exclusao automatica no banco de dados
#TODO Implementar menssagem direta em todos os alarmes 
