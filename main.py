import discord
import config

from config import LogType
from classes import OsuBot

# Grab config and string variables
CONFIGS = config.get_bot_configs()
STRINGS = config.get_bot_strings()


def main():
    # Retrieve bot token from .env or OS environment variables. (token_envar_name from configs)
    token = get_env_token(CONFIGS.token_envar_name)

    # Initialize bot
    for line in STRINGS.console_splash:
        print(line)

    # Construct bot activity object (activity.type and .name from configs)
    activity = discord.Activity(
        type=getattr(discord.ActivityType, CONFIGS.activity.type),
        name=CONFIGS.activity.name)

    # Construct ThmBOT object with configurations from configs, including command prefix
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
    bot.log(STRINGS.Run.login_start, LogType.WARN)
    try:
        bot.run(token)
    except discord.LoginFailure:
        bot.log(STRINGS.Run.login_fail)


def get_env_token(var_name):
    """Retrieves the bot's secret token from a .env or OS environment variables
    """
    from os import getenv
    from dotenv import load_dotenv

    load_dotenv()
    token = getenv(var_name)
    if not token:
        print(STRINGS.Token.not_found.format(var_name=var_name))
        raise EnvironmentError(f"'{var_name}' environmental variable undefined")
    else:
        return token


if __name__ == "__main__":
    main()
