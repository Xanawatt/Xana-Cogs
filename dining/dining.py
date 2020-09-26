from redbot.core import commands, checks, Config
import discord
import asyncio
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json

class Dining(commands.Cog):
	"""A Dining Cog"""
	def __init__(self, bot):
		"""Set up the plugin"""
		super().__init__()
		self.bot = bot

	async def getDateString(self):
		date_year = datetime.today().strftime('%Y')
		date_month = datetime.today().strftime("%m").lstrip("0")
		date_day = datetime.today().strftime("%d").lstrip("0")
		return f"{date_year}/{date_month}/{date_day}"
	
	
	@commands.command(name="getmeal")
	async def get_meal(self, ctx, str: dining_court):
		"""Gets the meal options from the provided dining court"""
		opts = Options()
		# opts.headless = True
		driver = webdriver.Firefox(options=opts)
		BASE_URL = 'https://dining.purdue.edu/menus/'
		
		dining_court = dining_court.lower().capitalize()
		meal = "Lunch"
		date_string = (await self.getDateString())
		URL = f"{BASE_URL}{dining_court}/{date_string}/{meal}"
		async with ctx.channel.typing():
		
			await driver.get(URL)
			items = (await driver.find_elements_by_xpath("/html/body/div[1]/div/div[2]/main/div[2]/div[2]")[0].text.split("\n"))

			dining_json = {
				'retrieved': str(datetime.now()),
				'dining_court': dining_court,
				'meal': meal,
				'stations': {}
			}
			last_station = ""
			if "Closed" in items[0]:
				dining_json['stations'] = "Closed"
				em = discord.Embed(title="Title", description=json.dumps(dining_json, indent=2, separators=(',', ': '), color=0x00ff00))
				ctx.channel.send(embed=em)
				return

			for item in items:
				if item.isupper():
					dining_json['stations'][item] = []
					last_station = item
				else:
					dining_json['stations'][last_station].append(item)

			em = discord.Embed(title="Title", description=json.dumps(dining_json, indent=2, separators=(',', ': '), color=0x00ff00))
			ctx.channel.send(embed=em)
			return

	async def send_message(self, channel: discord.TextChannel, message: str, delay=0.01):
		"""Sends a message to a channel with discord.typing()"""
		try:
			async with channel.typing():
				await asyncio.sleep(len(message) * delay)
				await self.bot.send_filtered(channel, content=message)
		except discord.Forbidden:
			pass  # Not allowed to send messages in this channel

