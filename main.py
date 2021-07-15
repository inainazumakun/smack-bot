import discord
import config

from config import LogType
from classes import OsuBot

# Grab config and string variables
CONFIGS = config.get_bot_configs()
STRINGS = config.get_bot_strings()


def main():
    # Retrieve bot token from .env or OS environment variables. (token_envar_name from configs)
    token = config.get_discord_token()

    # Initialize bot
    for line in STRINGS.console_splash:
        print(line)

    # Construct bot activity object (activity.type and .name from configs)
    activity = discord.Activity(
        type=getattr(discord.ActivityType, CONFIGS.activity.type),
        name=CONFIGS.activity.name)

    # Construct OsuBot object with configurations from configs, including command prefix
    bot = OsuBot(CONFIGS.command_prefix,
                 activity=activity,
                 status=CONFIGS.status)

    # Load startup cogs defined in configurations, but not disabled cogs.
    cogs_list = [cog for cog in CONFIGS.cogs if cog not in CONFIGS.disabled_cogs]
    bot.load_all_extension(cogs_list)

    # TODO
    # eventually replace this loading sequence with an actual formal loading process
    run(bot, token)


def run(bot, token):
    """Function for attempting a connection and login with the bot and Discord servers.
    """
    bot.log(STRINGS.Run.login_start_log, LogType.WARN)
    try:
        bot.run(token)
    except (discord.LoginFailure, RuntimeError) as e:
        bot.log(STRINGS.Run.login_fail_log.format(e=type(e).__name__), LogType.ERROR)
        bot.log((str(e)), LogType.ERROR)


if __name__ == "__main__":
    main()
