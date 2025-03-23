import discord
from discord.ext import commands
import dotenv
import os
import asyncio
import datetime
import game


dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True


client = commands.Bot(command_prefix="c/", intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    game.init(client)
    asyncio.create_task(scheduled_task())


@client.command(name="clongule")
async def send_message(ctx):
    view = game.GuessView()
    await ctx.send(f"Word: {game.day.word}\nIPA: {game.day.IPA}\nEnglish: {game.day.english}", view=view)


@client.command(name="test")
async def send_message(_):
    game.new_day()
    await alert_new_word()


async def scheduled_task():
    """Runs every day at 00:00"""
    while True:
        now = datetime.datetime.now()
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if now >= target_time:
            target_time += datetime.timedelta(days=1)

        sleep_seconds = (target_time - now).total_seconds() # calculate time until midnight
        await asyncio.sleep(sleep_seconds) # wait until midnight

        await alert_new_word() # once midnight, alert new word


async def alert_new_word():
    aisje_clongule_channel_id = 1347631529471508560
    clongule_channel = await client.fetch_channel(aisje_clongule_channel_id)
    await clongule_channel.send("New word available!!")


client.run(BOT_TOKEN)