import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View
import dotenv
import os

#import json

dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="c/", intents=intents)

class ClonguleModal(Modal, title='Clongule Test'):
    text_input = TextInput(
        label="Enter the message:",
        placeholder="Type something...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You sent: {self.text_input}")

class ModalButton(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Open Test Modal", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, _):
        modal = ClonguleModal()
        await interaction.response.send_modal(modal)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.command(name="clongule")
async def send_message(ctx):
    view = ModalButton()
    await ctx.send("Click the button to open the test Modal", view=view, ephemeral=True)


client.run(BOT_TOKEN)