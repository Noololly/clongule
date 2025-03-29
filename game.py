import asyncio
from typing import Optional
import discord
from discord.ui import Select, Button, View
from psql_connector import SQLConn
import time
import datetime


def init(bot: discord.client):
	"""
	Initialises the game so that all clongs and their words can be accessed by the program
	:return:
	"""
	global clongs, client

	client = bot

	conn = SQLConn()  #create the connection to the database
	cur = conn.conn.cursor()
	cur.execute("SELECT DISTINCT lang FROM clongule")  #get all individual clongs
	clongs = [row[0] for row in cur.fetchall()]  #format it into a usable format
	new_day()


def new_day():
	global day
	day = Day()


class Day:
	"""
	class that contains all the information about the word for that day
	:return:
	"""
	def __init__(self):
		self.conn = SQLConn()
		self.cur = self.conn.conn.cursor()
		self.clong = self.get_lang()
		self.word = self.get_word()
		self.IPA = self.get_ipa()
		self.english = self.get_english()
		self.is_cxei = self.get_is_cxei()


	def get_english(self):
		english_query = f"""
        SELECT eng FROM clongule
        WHERE word = %s
        LIMIT 1;
        """
		self.cur.execute(english_query, (self.word,))
		english = self.cur.fetchone()
		return english[0]


	def get_ipa(self) -> str: # gets IPA for the word of the day
		IPA_query = f"""
        SELECT ipa FROM clongule
        WHERE word = %s
        LIMIT 1;
        """
		self.cur.execute(IPA_query, (self.word,))
		ipa = self.cur.fetchone()
		return ipa[0]


	def get_word(self) -> str: # gets the word of the day
		word_query = f"""
        SELECT word FROM word
        WHERE lang = %s
        ORDER BY id DESC
        LIMIT 1;
        """
		self.cur.execute(word_query, (self.clong,))
		word = self.cur.fetchone()
		return word[0]


	def get_lang(self) -> str: # gets the clong for the day
		clong_query = """
            SELECT lang FROM word
            ORDER BY id DESC
            LIMIT 1;
            """
		self.cur.execute(clong_query)
		clong = self.cur.fetchone()
		return clong[0]


	def get_is_cxei(self):
		cxei_query = f"""
        SELECT cxei FROM clongule
        WHERE lang = %s
        LIMIT 1;
        """
		self.cur.execute(cxei_query, (self.clong,))
		is_cxei = self.cur.fetchone()
		return is_cxei[0]


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
			channel = interaction.channel
			user_id = interaction.user.id
			await validate_guess(clongs[int(selected)-1], channel, user_id) # selected is a number in a string for some dumb reason
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


async def validate_guess(guess, channel: discord.TextChannel, user_id: int):
	"""
	Function to validate the user's guess
	:param guess:
	:param channel:
	:param user_id:
	:return:
	"""

	user = await client.fetch_user(user_id)

	is_cxei_query = """
    SELECT cxei from clongule
    WHERE lang = %s
    LIMIT 1;
    """
	conn = SQLConn()
	cur = conn.conn.cursor()
	cur.execute(is_cxei_query, (guess,))
	is_cxei = cur.fetchone()[0]

	if user_id not in timed_out:
		if guess == day.clong:
			user = await client.fetch_user(user_id)
			await channel.send(f"{user.mention} Correct!")
			if user_id in user_guesses:
				del user_guesses[user_id]
			timed_out[user_id] = time.time()
		else:
			if user_id in user_guesses:
				user_guesses[user_id] = (user_guesses[user_id][0] + 1, time.time())
			else:
				user_guesses[user_id] = (1, time.time())

			if user_guesses[user_id][0] <= 2:
				await channel.send(f"""{user.mention} Incorrect! Try again. You are on guess {user_guesses[user_id][0]} out of 3. Cxei or not: {'🟩' if is_cxei and day.is_cxei or not is_cxei and not day.is_cxei else '⬛'}""")
			# ^^ sends the user a message telling them they are incorrect and how many guesses they have left and if their answer is correctly cxei or not

			else:
				await channel.send(f"{user.mention} Incorrect! Come back tomorrow!")
				del user_guesses[user_id]
				timed_out[user_id] = time.time()
	else:
		await channel.send(f"{user.mention} Come back tomorrow!")


async def remove_time_out_nanny():
	"""
	Function to wait until the next quarter of a day and then remove all users who have timed out
	:return:
	"""
	while True:
		now = datetime.datetime.now()
		if 0 <= now.hour < 6:
			target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
		elif 6 <= now.hour < 12:
			target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
		elif 12 <= now.hour < 18:
			target_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
		else:
			target_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

		sleep_time = (target_time - now).total_seconds()
		await asyncio.sleep(sleep_time)

		await remove_timed_out()


async def remove_timed_out():
	"""
	Removes all timed out users
	:return:
	"""
	current_time = time.time()
	timeout = 6 * 60 * 60 # 6 hour time out
	to_remove = [user_id for user_id, (_, last_guess_time) in user_guesses.items() if current_time - last_guess_time > timeout] # gets the users which have been inactive for over 6 hours
	for user_id in to_remove:
		del user_guesses[user_id]

	to_remove = [user_id for user_id, last_guess_time in timed_out.items() if current_time - last_guess_time > timeout] # gets the users which have been inactive for over 6 hours
	for user_id in to_remove:
		del timed_out[user_id]

day: Optional[Day] = None # tells intellisense to stop whining
client: Optional[discord.Client] = None

words = {}
clongs = []
user_guesses = {}
timed_out = {}