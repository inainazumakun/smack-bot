"""Osu Database Cog

"""
from discord.ext import commands
from config import LogType
import config
from pymongo import errors, MongoClient

CONFIGS = config.get_cog_configs('database')
STRINGS = config.get_cog_strings('database')


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_client = None
        self.db = None

    def connect(self):
        """Initializes the connection to a MongoDB database server as defined in database/configs.yml
        """
        # initialize database connection
        db_server = "mongodb://" + CONFIGS.host_name + ":" + CONFIGS.host_port + "/"
        self.bot.log(STRINGS.Connect.start_log.format(db_server=db_server),
                     LogType.WARN)
        db_client = MongoClient(db_server,
                                serverSelectionTimeoutMS=CONFIGS.connect_timeout)
        # Check and verify connection to database
        try:
            db_client.server_info()
            self.bot.log(STRINGS.Connect.success_log,
                         LogType.STATUS)
        except errors.ServerSelectionTimeoutError:
            # Connection timed out
            self.bot.log(STRINGS.Connect.fail_log,
                         LogType.ERROR)
            raise
        self.db_client = db_client
        self.db = db_client[CONFIGS.database_name]
        self.bot.log(self.bot.db)

    @commands.command()
    async def list_db(self, ctx):
        await ctx.send(self.db_client.list_database_names())


def setup(bot):
    cog = Database(bot)
    cog.connect()
    bot.add_cog(cog)
