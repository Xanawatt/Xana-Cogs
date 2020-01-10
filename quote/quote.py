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

	def import_file(self, file):
		with open(file, encoding="utf8") as f:
			lines = f.readlines()
			list = []
			for line in lines:
				if 'barlow_emote' in line:
					line = line.replace('barlow_emote', barlow_emote)
					list.append(line)

		return list

	def __init__(self, bot):
		"""Set up the plugin"""
		super().__init__()
		self.quote_file = 'quotes.txt'
		self.barlow_emote = '<:barlow:615621843130253314>'
		self.quote_list = import_file(quote_file)
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
		await quote_list.append(quote_to_add)

	"""
	# @quote.command(name="list")
	@commands.command(name="listquotes")
	async def quote_list(self, ctx):
		await ctx.maybe_send_embed(quote_list)
	"""

	@staticmethod
	def get_quote(ctx, quote_id):
		"""Get a random quote or supply a quote_id to get a quote"""
		if quote_id is None:
			# Get a random quote from quote_list
			random_int = random.randint(0, len(quote_list))
			return quote_list[random_int]
		else:
			# Gets a specific quote from quote_list based on quote_id
			ctx.channel.send(quote_id)
			if quote_id > len(quote_list) or quote_id < 0:
				# Fill this in with an actual error message
				return "That quote does not exist"
			else:
				return quote_list[quote_id]


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
