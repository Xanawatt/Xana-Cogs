from redbot.core import checks, Config, commands
import discord
import asyncio
import os
import random


class Mentioner(commands.Cog):
	"""A mentioning Cog"""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=30466642)
		default_guild = {
			"ignored_channels": [],
			"dm_roles": [],
		}
		self.config.register_guild(**default_guild)
	
	@checks.mod_or_permissions(manage_channels=True)
	@commands.group()
	async def mentionset(self, ctx):
		"""Mentioner settings"""
		pass
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="addchannel")
	async def add_channel(self, ctx, channel):
		"""Add a channel to get ignored"""
		try:
			if ctx.guild.get_channel(int(channel)) is None:
				raise ValueError
			channel_object = ctx.guild.get_channel(int(channel))
		except ValueError:
			if len(ctx.message.channel_mentions) > 0:
				for channel in ctx.message.channel_mentions:
					channel_object = channel
					break # only get the first, may change this later
			else: # must have entered a string
				await self.send_message(ctx, f"`{str(channel)}` is not a channel.")
				return # channel doesn't exist

		async with self.config.guild(ctx.guild).ignored_channels() as ignored_channels:
			if channel_object.id in ignored_channels: # can only store ints not objects
				await self.send_message(ctx, f"The {channel_object.mention} channel is already being ignored.")
				return
			ignored_channels.append(channel_object.id)
		await self.send_message(ctx, f"The {channel_object.mention} channel was ignored.")
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="removechannel")
	async def remove_channel(self, ctx, channel):
		"""Remove a channel that was previously ignored"""
		try:
			if ctx.guild.get_channel(int(channel)) is None:
				raise ValueError
			channel_object = ctx.guild.get_channel(int(channel))
		except ValueError:
			if len(ctx.message.channel_mentions) > 0:
				for channel in ctx.message.channel_mentions:
					channel_object = channel
					break # only get the first, may change this later
			else: # must have entered a string
				await self.send_message(ctx, f"`{str(channel)}` is not a channel.")
				return # channel doesn't exist
		
		async with self.config.guild(ctx.guild).ignored_channels() as ignored_channels:
			if channel_object.id not in ignored_channels: # can only store ints not objects
				await self.send_message(ctx, f"The {channel_object.mention} channel was not being ignored.")
				return
			ignored_channels.remove(channel_object.id)
		await self.send_message(ctx, f"The {channel_object.mention} channel will no longer be ignored.")
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="addrole")
	async def add_role(self, ctx, role): # copy pasted from add/remove channel
		"""Add a role that will be dm'd on role ping"""
		try:
			if ctx.guild.get_role(int(role)) is None:
				raise ValueError
			role_object = ctx.guild.get_role(int(role))
		except ValueError:
			if len(ctx.message.role_mentions) > 0:
				for role in ctx.message.role_mentions:
					role_object = role
					break # only get the first, may change this later
			else: # must have entered a string
				await self.send_message(ctx, f"`{str(role)}` is not a role.")
				return # role doesn't exist

		async with self.config.guild(ctx.guild).dm_roles() as dm_roles:
			if role_object.id in dm_roles: # can only store ints not objects
				await self.send_message(ctx, f"The {role_object.name} role is already configured for getting dms.") # don't use mention for roles, because ping bad
				return
			dm_roles.append(role_object.id)
		await self.send_message(ctx, f"The {role_object.name} role will now get dms.")
	
	@checks.mod_or_permissions(manage_channels=True)
	@mentionset.command(name="removerole")
	async def remove_role(self, ctx, role):
		"""Remove a role that previously got dm'd on role ping"""
		try:
			if ctx.guild.get_role(int(role)) is None:
				raise ValueError
			role_object = ctx.guild.get_role(int(role))
		except ValueError:
			if len(ctx.message.role_mentions) > 0:
				for role in ctx.message.role_mentions:
					role_object = role
					break # only get the first, may change this later
			else: # must have entered a string
				await self.send_message(ctx, f"`{str(role)}` is not a role.")
				return # role doesn't exist
		
		async with self.config.guild(ctx.guild).dm_roles() as dm_roles:
			if role_object.id not in dm_roles: # can only store ints not objects
				await self.send_message(ctx, f"The {role_object.name} role was not configured for getting dms.") 
				return
			dm_roles.remove(role_object.id)
		await self.send_message(ctx, f"The {role_object.name} role will no longer get dms.")
	
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
				await self.send_message(message.channel, f"There's nobody else in the {role.name} role :(")
				return

			num_dmd = 0
			dm_members_list = ""
			for member in role.members:
				for role in member.roles:
					if role.id in (await self.config.guild(message.guild).dm_roles()) and message.author != member:
						dm_members_list += member.name + ', '
						num_dmd += 1
						try:
							dmchannel = await member.create_dm()
							await dmchannel.send(f'{message.author} needs your help in {message.channel.mention}!')						
						except AttributeError:
							await self.send_message(message.channel, 'failed to send dm') # This error should probably be logged instead of sent in a channel
			if num_dmd > 0:
				await self.send_message(message.channel, str(member_count) + " user(s) were notified; " + dm_members_list + "was notified via DM.")
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
