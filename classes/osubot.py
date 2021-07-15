import inspect
from pathlib import PurePath

import discord.ext.commands

from config import LogType, Log
from discord.ext.commands import Bot
from datetime import datetime


class OsuBot(Bot):
    """Custom discord.Bot subclass for better control over client functionality
    """
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    def log(self, message, log_type=LogType.DEBUG):
        """Custom event to pass messages into logger.py for development logging and debugging purposes
        Debug log actions and logic are performed in the logger cog
        :parameter
        message=:class:`str`
            Message string to pass into console/debug chat channel
        verbosity=:class:`config.LOG data class`
            Log messaging classification, taken from config.LOG to signify
            message's severity and importance.
        """
        # retrieve current frame, then backtrack to the previous frame's code's caller
        caller = inspect.currentframe().f_back.f_code

        origin = PurePath(caller.co_filename).stem  # naked file name of caller
        func = caller.co_name  # name of function calling bot.log()
        line = caller.co_firstlineno  # line number of bot.log() message
        timestamp = str(datetime.utcnow()) + " UTC"

        # Construct log data object to dispatch out in a log event
        log = Log(origin=origin,
                  message=message,
                  log_type=log_type.tag,
                  timestamp=timestamp,
                  line=line,
                  func=func,
                  tag_color=log_type.tag_color,
                  message_color=log_type.message_color,)
        # Broadcast event to all event listeners - calls cog.on_log() functions
        self.dispatch('log', log)

    def load_extension(self, name, **kwargs):
        """bot.load_extension() event wrapper to broadcast success/failure states
        """
        try:
            super().load_extension(name)
            # Dispatch event with parameters ``cog_name`` and ``error`` (if any)
            self.dispatch('load_extension', name, False)
        except Exception as failed:
            self.dispatch('load_extension', name, failed)
            raise

    def load_all_extension(self, ext_list, **kwargs):
        """A quick script to quickly load several extensions at once.
        """
        for cog in list(ext_list):
            self.log(f"Loading extension '{cog}'", LogType.WARN)
            self.load_extension(cog, **kwargs)

    def db(self):
        cog = self.get_cog('Database')
        if cog:
            return cog
        else:
            raise discord.ext.commands.ExtensionNotLoaded('Database cog is not running')

