"""Osu API Cog

"""
from discord.ext import commands
from config import LogType
import config
import aiohttp

CONFIGS = config.get_cog_configs('api')
STRINGS = config.get_cog_strings('api')
URLS = CONFIGS.api
# Defining headers to ensure responses from API are only in json
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


class OsuApi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = None
        self.token_expires_in = None
        self.token_type = None
        self.__client = None

    async def request_auth(self):
        """Attempts to request API authentication and authorization, and store token data.
        """
        # Generate credentials and parameters for the API authorization request.
        credentials = config.get_api_credentials()
        payload = {  # required parameters for osu!api token authentication
            'client_id': int(credentials.id),
            'client_secret': credentials.secret,
            'grant_type': URLS.Params.auth.grant_type,
            'scope': URLS.Params.auth.scope,
        }
        # Make the authorization request with API credentials provided.
        url = URLS.auth
        self.bot.log(STRINGS.Auth.start_log.format(url=url), LogType.WARN)
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.post(url, json=payload) as response:
                response = await response.json()

        # Check if response is valid, and store token data
        if len(response) is 3:  # if somebody has a better way to check auth please help
            self.token = response['access_token']
            self.token_expires_in = response['expires_in']
            self.token_type = response['token_type']
            self.bot.log(STRINGS.Auth.success_log, LogType.STATUS)
        else:
            try:
                error = response['error']
            except KeyError:
                error = STRINGS.Auth.error_log.format(error=str(response))
            self.bot.log(STRINGS.Auth.fail_log, LogType.ERROR)
            self.bot.log(error, LogType.ERROR)
            raise RuntimeWarning

    async def client(self):
        headers = HEADERS

        # Assign auth token to headers; request auth if nonexistent
        if not self.token:
            try:
                await self.request_auth()
                headers['Authorization'] = self.token_type + ' ' + self.token
            except Exception:
                self.bot.log(STRINGS.Client.fail_log, LogType.WARN)
                raise

        # Create a new client if .__client doesn't exist already
        if not isinstance(self.__client, aiohttp.ClientSession):
            self.bot.log(STRINGS.Client.create_log, LogType.WARN)
            self.__client = aiohttp.ClientSession(headers=headers)
            self.bot.log(STRINGS.Client.success_log, LogType.STATUS)

        return self.__client

    async def fetch(self, url, params=None, client=None):
        if client:
            session = client
        else:
            session = await self.client()
        async with session.get(url, params=params) as response:
            self.bot.log(STRINGS.Fetch.start_log.format(url=url))
            return await response.json()

    @commands.command()
    async def auth_api(self, ctx):
        await ctx.send("Generating API token...")
        await self.request_auth()

    @commands.command()
    async def recent(self, ctx, message):
        await ctx.send(await self.fetch(URLS.recent.format(user=message)))


def setup(bot):
    bot.add_cog(OsuApi(bot))
