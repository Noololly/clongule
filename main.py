import discord
from discord.ext import commands
import dotenv
import os
import asyncio
import datetime
import game
import lang_getter_worker

dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True


client = commands.Bot(command_prefix="c/", intents=intents)


@client.event
async def on_ready():
	print(f"Logged in as {client.user}")
	game.init(client)


@client.command(name="clongule")
async def send_message(ctx):
	view = game.GuessView()
	await ctx.send(f"Word: {game.day.word}\nIPA: {game.day.IPA}\nEnglish: {game.day.english}", view=view)


@client.command(name="reset")
async def send_message(_):
	lang_getter_worker.get_word()
	game.new_day()
	await alert_new_word()


async def alert_new_word():
	aisje_clongule_channel_id = 1347631529471508560
	clongule_channel = await client.fetch_channel(aisje_clongule_channel_id)
	await clongule_channel.send("New word available!!")


client.run(BOT_TOKEN)