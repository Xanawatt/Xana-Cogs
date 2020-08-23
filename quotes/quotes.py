from redbot.core import commands, checks, Config
import discord
import asyncio
import random

# TODO:
#  standardize quote symbols
#  embed listquotes
#  Per guild support

class Quotes(commands.Cog):
	"""A quote Cog"""
	def __init__(self, bot):
		"""Set up the plugin"""
		super().__init__()
		self.config = Config.get_conf(self, identifier=1234567890)
		default_global = {
			"quote_list": [],
		}
		self.config.register_global(**default_global)
		self.bot = bot
	
	@commands.group()
	async def quotes(self, ctx):
		"""Quotes!"""
		pass

	@quotes.command()
	async def get(self, ctx, quote_id: int):
		"""Get a quote with an index"""
		quote_list = await self.config.quote_list()
		if quote_id >= len(quote_list):
			await self.send_message(ctx.channel, '`Quote #' + str(quote_id) + '` does not exist.')
		else:
			quote = (await self.config.quote_list())[quote_id]
			await self.send_message(ctx.channel, quote)

	@quotes.command()
	async def random(self, ctx):
		"""Get a random quote"""
		quote_list = await self.config.quote_list()
		await self.send_message(ctx.channel, quote_list[random.randint(0, len(quote_list) - 1)])

	@quotes.command()
	async def list(self, ctx):
		"""List all quotes"""
		message = "Quote list:" + "\n" + "```" + "\n"
		quote_list = await self.config.quote_list()
		for index, quote in enumerate(quote_list):
			message += str(index) + ". " + quote + "\n"
		message += "```"
		await self.send_message(ctx.channel, message, delay=0)

	@checks.mod_or_permissions(manage_channels=True)
	@quotes.command()
	async def add(self, ctx, *, quote_to_add: str): # The * is important so not just the first word gets taken
		"""Adds a quote to the quote list"""
		async with self.config.quote_list() as quote_list:				
			quote_list.append(quote_to_add)
		await self.send_message(ctx.channel, "Added the quote: `" + quote_to_add + "`")

	@checks.mod_or_permissions(manage_channels=True)
	@quotes.command()
	async def delete(self, ctx, quote_id: int):
		"""Deletes a quote given an index and moves up the quotes after, changing their indecies"""
		quote_list_before = await self.config.quote_list()
		if quote_id >= len(quote_list):
			await self.send_message(ctx.channel, '`Quote #' + str(quote_id) + '` does not exist.')
		else:
			async with self.config.quote_list() as quote_list:
				quote_list.pop(quote_id)
			await self.send_message(ctx.channel, 'Quote #' + str(quote_id) + ': `' + quote_list[quote_id] + '` was deleted.')

	@checks.mod_or_permissions(manage_channels=True)
	@quotes.command()
	async def edit(self, ctx, quote_id: int, *, text_to_replace):
		"""Edit a quote"""
		quote_list_before = await self.config.quote_list()
		if quote_id >= len(quote_list_before):
			await self.send_message(ctx.channel, '`Quote #' + str(quote_id) + '` does not exist.')
		else:
			async with self.config.quote_list() as quote_list:
				quote_list[quote_id] = text_to_replace
			await self.send_message(ctx.channel, 'Quote #' + str(quote_id) + ': `' + quote_list_before[quote_id] + '` was edited to: `' + text_to_replace + '`')

	async def send_message(self, channel: discord.TextChannel, message: str, delay=0.01):
		"""Sends a message to a channel with discord.typing()"""
		try:
			async with channel.typing():
				await asyncio.sleep(len(message) * delay)
				await self.bot.send_filtered(channel, content=message)
		except discord.Forbidden:
			pass  # Not allowed to send messages in this channel

