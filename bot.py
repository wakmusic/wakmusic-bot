import json
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print("봇 구동 시작")


bot.load_extension('extensions.news')
bot.load_extension('extensions.lyrics')
bot.load_extension('extensions.playlist')
with open('config.json', encoding='utf-8-sig') as file:
    js = json.load(file)
bot.run(js['token'], reconnect=True)
