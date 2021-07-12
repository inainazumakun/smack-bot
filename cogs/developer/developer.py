"""Developer Cog

A utility cog with commands intended for developers to assist in testing bot functionality
and development.
"""
from discord.ext import commands
from discord.ext.commands import errors
import config
from config import LogType

# CONFIGS = config.get_cog_configs('developer')
STRINGS = config.get_cog_strings('developer')


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def log(self, ctx, log_type, message=''):
        """!log <log_type=DEBUG> <message> - Chat command to send a bot log message.
        """
        try:
            log_type = getattr(LogType, log_type)
        except AttributeError:
            message = log_type + " " + message
            log_type = LogType.DEBUG

        user = ctx.message.author
        log_message = STRINGS.log.format(user=user, message=message)
        self.bot.log(log_message, log_type)

    @commands.command()
    async def reload(self, ctx, ext):
        """!reload <ext_name> - Chat command to reload an extension or cog
        Extensions in the cog folder require `cogs.` prefix path, i.e. '!reload cogs.developer'
        """
        try:  # Attempt to reload extension or cog
            self.bot.log(STRINGS.Reload.reloading_log.format(ext=ext), LogType.WARN)
            self.bot.reload_extension(ext)
            await ctx.send(STRINGS.Reload.reload_reply.format(ext=ext))

        except errors.DiscordException as e:
            load_fail = STRINGS.Reload.load_fail_log.format(e=type(e).__name__)
            self.bot.log(load_fail, LogType.ERROR)
            self.bot.log(e, LogType.ERROR)


def setup(bot):
    bot.add_cog(Developer(bot))
