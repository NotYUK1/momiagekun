import discord
from discord.ext import commands
import subprocess
import ffmpeg
from voice_generator import creat_WAV
import os

client = commands.Bot(command_prefix='-')
voice_client = None
token = os.environ['DISCORD_BOT_TOKEN']

@client.command()
async def hip(ctx):
    #voicechannelを取得
    vc = ctx.author.voice.channel
    #voicechannelに接続
    await vc.connect()

@client.command()
async def hop(ctx):
    #切断
    await ctx.voice_client.disconnect()

@client.event
async def on_message(message):
    if message.content.startswith('-'):
        pass

    else:
        if message.guild.voice_client:
            #print(message.content)
            creat_WAV(message.content)
            source = discord.FFmpegPCMAudio("output.wav")
            message.guild.voice_client.play(source)
        else:
            pass
    await client.process_commands(message)

client.run(token)