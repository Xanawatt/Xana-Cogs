from redbot.core import commands
import discord
import asyncio
import random


# quote_file = "quotes.txt"
# barlow_emote = '<:barlow:615621843130253314>'

'''
quote_list = ['"YEE-HAW" ' + barlow_emote,
				'"BAZINGA!" ' + barlow_emote,
				'"Questions, comments, concerns, threats of violence, offers of bribes?" ' + barlow_emote,
				'"mmmhh" ' + barlow_emote,
				'"Ya' + 'll a bunch of dummies" ' + barlow_emote,
				'"Keep your hands off my attributes"' + barlow_emote
				]
'''




class Quote(commands.Cog):
	"""My custom cog"""
	# Add the ability to add and remove quotes by command

	def __init__(self, bot):
		"""Set up the plugin"""
		super().__init__()
		self.quote_file = '/home/xanawatt/Xana-Cogs/quote/quotes.txt'  # Change to relative path later
		self.barlow_emote = '<:barlow:615621843130253314>'

		with open(self.quote_file, encoding="utf8") as f:
			lines = f.readlines()
			list = []
			for line in lines:
				if 'barlow_emote' in line:
					line = line.replace('barlow_emote', self.barlow_emote)
					list.append(line)

		self.quote_list = list  # The above code could be changed to a method, but I couldn't figure out how
		self.bot = bot

	# @commands.group()
	@commands.command()
	async def quote(self, ctx, quote_id: int):
		await self.send_message(ctx.channel, self.get_quote(ctx, quote_id))

	@commands.command(name="randomquote")
	async def quote_random(self, ctx):
		await self.send_message(ctx.channel, self.get_quote(ctx, None))

	@commands.command(name="addquote")
	async def quote_add(self, ctx, *, quote_to_add: str):
		save_quote_to_file(quote_to_add)
		await self.quote_list.append(quote_to_add)


	def save_quote_to_file(self, quote_to_add):
		with open(self.quote_file, encoding="utf8") as f:
			f.write("\n" + quote_to_add)


	"""
	# @quote.command(name="list")
	@commands.command(name="listquotes")
	async def quote_list(self, ctx):
		await ctx.maybe_send_embed(quote_list)
	"""

	def get_quote(self, ctx, quote_id):
		"""Get a random quote or supply a quote_id to get a quote"""
		if quote_id is None:
			# Get a random quote from quote_list
			random_int = random.randint(0, len(self.quote_list))
			return self.quote_list[random_int]
		else:
			# Gets a specific quote from quote_list based on quote_id
			ctx.channel.send(quote_id)
			if quote_id > len(self.quote_list) or quote_id < 0:
				# Fill this in with an actual error message
				return "That quote does not exist"
			else:
				return self.quote_list[quote_id]


	async def send_message(self, channel: discord.TextChannel, message: str):
		"""
		Send a mwessage to a channew.
		Wiww send a typing indicatow, and wiww wait a vawiabwe amount of time
		based on the wength of the text (to simuwate typing speed)
		"""
		try:
			async with channel.typing():
				await asyncio.sleep(len(message) * 0.01)
				await self.bot.send_filtered(channel, content=message)
		except discord.Forbidden:
			pass  # Not awwowed to send mwessages in dis channel

