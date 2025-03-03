import discord

from discord.ui import Select, Button, View
from psqltest import SQLConn

words = {}
clongs = []


def init():
    """
    Initialises the game so that all clongs and their words can be accessed by the program
    :return:
    """
    global clongs

    conn = SQLConn()  #create the connection to the database
    cur = conn.conn.cursor()
    cur.execute("SELECT DISTINCT lang FROM clongule")  #get all individual clongs
    clongs = [row[0] for row in cur.fetchall()]  #format it into a usable format


class GuessButton(Button):
    """
    A class that contains the submit button
    :return:
    """

    def __init__(self, parent_view):
        super().__init__(label="Submit", style=discord.ButtonStyle.success)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        selected = self.parent_view.guess.selected_value
        if selected:
            await interaction.response.defer()
            await interaction.user.send(f"You sent: {clongs[int(selected) - 1]}")
        else:
            await interaction.response.send_message("Select an option first!", ephemeral=True)


class Guess(Select):
    """
    A class that contains the clong selection list
    :return:
    """

    def __init__(self):
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="Select your guess...",
            options=[discord.SelectOption(label=clong, value=str(i + 1)) for i, clong in enumerate(clongs)]
        )
        self.selected_value = None

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_value = self.values[0]


class GuessView(View):
    """
    A class that allows all the components of a guess to be sent in one message, and so that they can interact with each other
    :return:
    """

    def __init__(self):
        super().__init__()
        self.guess = Guess()
        self.add_item(self.guess)
        self.add_item(GuessButton(self))
