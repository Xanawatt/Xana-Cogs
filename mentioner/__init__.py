from .mentioner import Mentioner


def setup(bot):
    n = Mentioner(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
