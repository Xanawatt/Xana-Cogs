# -*- coding: utf-8 -*-
import re
from redbot.core import checks, Config
import discord
from redbot.core import commands
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
import asyncio
import datetime
import os
import aiohttp
from redbot.core.i18n import Translator, cog_i18n
from io import BytesIO
import functools
import textwrap
import random


# TODO:
#  Don't mention in certain channels



class Mentioner(commands.Cog):
	"""A mentioning Cog"""

	def __init__(self, bot):
		self.bot = bot
		self.loop = self.bot.loop.create_task(self.start())
		self.restart = True
		self.defaultrole = "New"
		self._session = aiohttp.ClientSession()
		self.config = Config.get_conf(self, identifier=1234567890)
		default_global = {
			"ignored_channels": [],
		}
		self.config.register_global(**default_global)

	def cog_unload(self):
		self.bot.remove_listener(self.listener)
		asyncio.get_event_loop().create_task(self._session.close())
		self.loop.cancel()

	async def start(self):
		await self.bot.wait_until_ready()
		while True:
			if not self.restart:
				guilds = self.bot.guilds
				for i in guilds:
					profils = await self.profiles.data.all_members(i)
					for j in profils.keys():
						member = i.get_member(j)
						if member is None:
							await self._reset_member(i, j)
						else:
							await self.profiles.data.member(member).today.set(0)
				self.restart = True
			if datetime.datetime.now().strftime("%H:%M") in [
				"05:00",
				"05:01",
				"05:02",
				"05:03",
				"05:04",
				"05:05",
			]:
				self.restart = False
			await asyncio.sleep(30)
	
	@checks.mod_or_permissions(manage_channels=True)
	@commands.group()
	async def mentionset(self, ctx):
		pass
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="add")
	async def mentionset_add(self, ctx, *, channel_id:int):
		"""Add a channel to get ignored"""
		async with self.config.ignored_channels() as ignored_channels:
			ignored_channels.append(channel_id)
		await send_message(ctx, "The " + str(channel_id) + " channel was ignored.")
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="remove")
	async def mentionset_remove(self, ctx, *, channel_id:int):
		"""Remove a channel that was previously ignored"""
		async with self.config.ignored_channels() as ignored_channels:
			ignored_channels.remove(channel_id)
		await ctx.send("The " + str(channel_id)+ " channel was removed.")

	async def listener(self, message):
		if message.channel.id in (await self.config.ignored_channels()):
			return
		if type(message.author) != discord.Member:
			# throws an error when webhooks talk, this fixes it
			return
		if type(message.channel) != discord.channel.TextChannel:
			return
		if message.author.bot:
			return

		if message.role_mentions is None:
			return
		
		roles = message.role_mentions
		for role in roles:
			member_count = 0
			for member in role.members:
				member_count += 1
			if len(role.members) < 1:
				async with message.channel.typing():
					# do expensive stuff here
					await message.channel.send(f"There's nobody else in the {role.name} role :(")
					return

			num_tutors = 0
			tutor_list = ""
			for member in role.members:
				for role in member.roles:
					if 'Tutor' in role.name and message.author != member:
						tutor_list += member.name + ', '
						num_tutors += 1
						try:
							dmchannel = await member.create_dm()
							await dmchannel.send(f'{message.author} needs your help in {message.channel.mention}!')						
						except AttributeError:
							await message.channel.send('failed to send dm')
			if num_tutors > 0:
				await message.channel.send(str(member_count) + " user(s) were notified; " + tutor_list + "was notified via DM.")
				return
			else:
				await message.channel.send(str(member_count) + " user(s) were notified.")
				return

	async def send_message(self, channel: discord.TextChannel, message: str, delay=0.01):
		"""Sends a message to a channel with discord.typing()"""
		try:
			async with channel.typing():
				await asyncio.sleep(len(message) * delay)
				await self.bot.send_filtered(channel, content=message)
		except discord.Forbidden:
			pass  # Not allowed to send messages in this channel
