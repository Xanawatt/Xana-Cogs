from redbot.core import commands
import discord
import asyncio

class Replace(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        """Set up the plugin"""
        super().__init__()
        self.bot = bot

    @commands.command()
    async def replace(self, ctx: commands.Context, from_this, to_that):
        """Replace a word in the previous message with a different word."""
        """
        from_this = args.split(" ")[0]
        to_that = args.split(" ")[1]
        """
        message = (await ctx.channel.history(limit=2).flatten())[1].content
        if not message:
            message = "I can't replace that!"
        message_to_send = self.replace_string(message, from_this, to_that)
        await self.send_message(ctx.channel, message_to_send)

    @staticmethod
    def replace_string(message, from_this, to_that):
        if from_this.lower() not in message.lower():
            return "Requested word to replace is not in last message."

        return message.replace(from_this, to_that)


    async def send_message(self, channel: discord.TextChannel, message: str):
        """Send a mwessage to a channew.
        Wiww send a typing indicatow, and wiww wait a vawiabwe amount of time
        based on the wength of the text (to simuwate typing speed)
        """
        try:
            async with channel.typing():
                await asyncio.sleep(len(message) * 0.01)
                await self.bot.send_filtered(channel, content=message)
        except discord.Forbidden:
            pass  # Not awwowed to send mwessages in dis channew
