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
		self.config = Config.get_conf(self, identifier=30466642)
		default_global = {
			"ignored_channels": [],
		}
		default_guild = {
			"ignored_channels": [],
		}
		self.config.register_global(**default_global)
		self.config.register_guild(**default_guild)
		

	def cog_unload(self):
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
		"""Mentioner settings"""
		pass
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command()
	async def add(self, ctx, channel):
		"""Add a channel to get ignored"""
		if ctx.message.channel_mentions is not None and ctx.guild.get_channel(channel) is None:
			channel_object = channel
		elif ctx.message.channel_mentions is None and ctx.guild.get_channel(channel) is not None:
			channel_object = ctx.guild.get_channel(channel)
		else: # both are none
			await self.send_message(ctx, f"`{str(channel)}` is not a channel.")
			return # channel doesn't exist

		async with self.config.guild(ctx.guild).ignored_channels() as ignored_channels:
			if channel_object in ignored_channels:
				await self.send_message(ctx, f"The {channel_object.mention} channel is already being ignored.")
				return
			ignored_channels.append(channel_object)
		await self.send_message(ctx, f"The {channel_object.mention} channel was ignored.")
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command()
	async def remove(self, ctx, channel):
		"""Remove a channel that was previously ignored"""
		if ctx.message.channel_mentions is not None and ctx.guild.get_channel(channel) is None:
			for channel in ctx.message.channel_mentions:
				channel_object = channel
				break # only get the first, may change this later
		elif ctx.message.channel_mentions is None and ctx.guild.get_channel(channel) is not None:
			channel_object = ctx.guild.get_channel(channel)
		else: # both are none
			await self.send_message(ctx, f"`{str(channel)}` is not a channel.")
			return # channel doesn't exist
			
		async with self.config.guild(ctx.guild).ignored_channels() as ignored_channels:
			if channel_object not in ignored_channels:
				await self.send_message(ctx, f"The {channel_object.mention} channel was not being ignored.")
				return
			ignored_channels.remove(channel_object)
		await self.send_message(ctx, f"The {channel_object.mention} channel will no longer be ignored.")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel.id in (await self.config.guild(message.guild).ignored_channels()):
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
			if len(role.members) <= 1:
				async with message.channel.typing():
					# do expensive stuff here
					await self.send_message(message.channel, f"There's nobody else in the {role.name} role :(")
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
							await self.send_message(message.channel, 'failed to send dm') # This error should probably be logged instead of sent in a channel
			if num_tutors > 0:
				await self.send_message(message.channel, str(member_count) + " user(s) were notified; " + tutor_list + "was notified via DM.")
				return
			else:
				await self.send_message(message.channel, str(member_count) + " user(s) were notified.")
				return

	async def send_message(self, channel: discord.TextChannel, message: str, delay=0.01):
		"""Sends a message to a channel with discord.typing()"""
		try:
			async with channel.typing():
				await asyncio.sleep(len(message) * delay)
				await self.bot.send_filtered(channel, content=message)
		except discord.Forbidden:
			pass  # Not allowed to send messages in this channel
