from .mentioner import Mentioner


def setup(bot):
    n = Mentioner(bot)
    bot.add_cog(n)
