"""Logger Cog

A utility cog with the purpose of listening to bot and server events and responding to them
by logging them to the console or specific discord channels.
"""
from discord.ext import commands
from config import LogType
import config

CONFIGS = config.get_cog_configs('logger')
STRINGS = config.get_cog_strings('logger')


class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_cache = list()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Listener for all successful command invocation attempts
        """
        invoke_log = STRINGS.command_log.format(
            user=ctx.author, msg=ctx.message.content)
        self.bot.log(invoke_log, LogType.INVOKE)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Listener for failed or nonexistent command invocations
        """
        if isinstance(error, commands.CommandNotFound):
            message = STRINGS.command_not_found_log.format(
                user=ctx.author, e=type(error).__name__, msg=ctx.message.content)
            self.bot.log(message, LogType.INFO)
        else:
            invoke_log = STRINGS.command_log.format(
                user=ctx.author, msg=ctx.message.content)
            self.bot.log(invoke_log, LogType.WARN)
            error_message = STRINGS.command_error_log.format(
                error=error
            )
            self.bot.log(error_message, LogType.ERROR)

    @commands.Cog.listener()
    async def on_log(self, log):
        """Listener for bot.log() to log message and notify terminal/channels"""
        await self.log_message(log)

    @commands.Cog.listener()
    async def on_load_extension(self, extension, failed):
        """Listener for bot.load_extension"""
        if failed:
            self.bot.log(STRINGS.Ext.load_fail_log.format(
                failed=str(failed), extension=extension
            ), LogType.ERROR)
        else:
            self.bot.log(STRINGS.Ext.load_success_log.format(
                extension=extension
            ), LogType.STATUS)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.log(STRINGS.bot_ready_log, LogType.STATUS)

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.bot.log(STRINGS.bot_disconnect_log, LogType.ERROR)

    async def log_message(self, log):
        """Logs developer messages to the console and chat channels."""
        # TODO: need to code a way to check if verbosity level is allowed to print
        # for now, everything goes
        # TODO: eventually also print to a discord channel
        self.logs_cache.append(log)
        # Checks if the log is an ERROR log, and will color log message text if so
        print(log)


def setup(bot):
    bot.add_cog(Logger(bot))
