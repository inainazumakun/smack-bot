"""Bot & Cog Configuration Module

This module allows code to parse and import variables from YAML files for usage
as user-configurable variables, default values, and strings. Can handle nested
values and data types of any kind. All data will be exported as a data class
object containing the values within the configuration file that can be used as
their respective value's data type. Dictionaries are not created due to nested
data classes being created instead. You can convert into a tuple/dict with the
provided methods of config.to_dict() and config.to_tuple().
Only .yml files are supported for standardization of filenames.

!WARNING!: there may be unintended and unexpected effects if all non-list values
           in the .yml file do not have keys/labels!

Module is also where the log enum class is found for properly sending logs for
development and debugging purposes.

    Example:
# cogs/my_cog/configs.yaml
---
web_url: 'www.tryhackme.com'
doge_number: 2
example_list:
    - 1
    - 2
    - 3
example_nest:
    word1: 'hello '
    word2: world
...

# cogs/my_cog/main.py
import config
my_config = config.get_cog_configs('my_cog')

> print(my_config.web_url)
> www.tryhackme.com
> print(my_config.doge_number)
> 2
> print(my_config.doge_number + 1)
> 3
> print(my_config.example_list[0])
> 1
> print(my_config.example_nest.word1 + my_config.example_nest.word2)
> hello world

This module only works with YAML (.yml or .yaml) files.

Requires `yaml` to be installed in the Python environment you are using this file with.

When imported, this module contains
the following main functions:
---------------
    get_cog_configs(cog_name=:class:`str`)
        Returns a data class struct containing /cogs/cog_name/configs.yml values.
    get_cog_strings(cog_name=:class:`str`)
        Returns a data class struct containing /cogs/cog_name/strings.yml values.
    generate_classes(obj=:class:`dict`)
        Outputs a recursively generated data class object from dictionaries
"""
import yaml
from dataclasses import dataclass, make_dataclass

# Path template for .yml files
BOT_CONFIGS_PATH = "bot_configs.yml"
BOT_STRINGS_PATH = "bot_strings.yml"

COG_STRINGS_PATH = "cogs/{}/strings.yml"
COG_CONFIGS_PATH = "cogs/{}/configs.yml"


@dataclass
class LogType:
    """Definition of various log types for bot.log()
    """

    @dataclass
    class Tag:
        tag: str
        tag_color: str = '\u001b[0m'
        message_color: str = '\u001b[0m'

    ERROR = Tag('!',  # errors & exceptions
                tag_color='\u001b[31m',
                message_color='\u001b[31m')
    DEBUG = Tag('%',  # debug prints and statements
                tag_color='\u001b[36m')

    WARN = Tag('*',  # warnings
               tag_color='\u001b[33m',
               message_color='\u001b[33m')
    STATUS = Tag('#',  # successful state changes
                 tag_color='\u001b[34m',
                 message_color='\u001b[32m')
    INFO = Tag('.',  # miscellaneous statistics
               tag_color='\u001b[37m',
               message_color='\u001b[37m')
    INVOKE = Tag('-',  # command being invoked by a user
                 tag_color='\u001b[32m',
                 message_color='\u001b[37m')


@dataclass
class Log:
    """Data structure object to represent a log message and various statistics/information
    """
    origin: str
    message: str
    log_type: str
    timestamp: str
    line: int
    func: str
    tag_color: str = "\u001b[0m"  # defaults to gray
    message_color: str = "\u001b[0m"  # defaults to gray

    def __repr__(self):
        """Automatically format Log objects to be represented in a pure string
        """
        return f"{self.timestamp} [{self.log_type}]{self.origin}[{self.line}]." \
               f"{self.func}: {self.message}"

    def __str__(self):
        """Automatically format Log objects to be printed into a terminal
        """
        # adds {tag_color} and {message.color}
        return f"{self.timestamp} " \
               f"[{self.tag_color}{self.log_type}\u001b[0m]" \
               f"{self.origin}[{self.line}].{self.func}: " \
               f"{self.message_color}{self.message}\u001b[0m"


def read_yml(path):
    """Opens and reads a YAML (.yml ONLY) file
    """
    try:
        with open(path, 'r') as file:
            stream = yaml.load(file.read(), Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("CONFIG ERROR: 'path' not found! Maybe check the name of the file.")
    return stream


def generate_classes(obj):
    """Recursively convert dictionaries into a nested data class
    :parameter:obj:`dict`
        Input dictionary for conversion
    :returns:class:`Config`
        Data class object that stores all keys as attributes, with the values
        being the corresponding input dictionary's key value.
    """
    if not isinstance(obj, dict):
        raise TypeError("generate_classes() input must be type dict")
    return _generate_classes(obj)


def _generate_classes(obj):
    """Inner recursive function for converting dict into tuples, then nested data classes."""
    # make_dataclass() does not like dicts and lists as fields,
    # so recursively call again on dictionaries and cast lists
    # into tuples
    result = []
    for key, value in obj.items():
        if isinstance(value, dict):
            value = _generate_classes(value)
        elif isinstance(value, list):
            value = tuple(value)
        result.append((key, None, value))
    return make_dataclass('Config', result, frozen=True)


def get_cog_configs(cog_name):
    """Parses cogs/<cog_name>/configs.yml into a usable data structure.

    :param:cog_name:`str`
        Name of the cog package (do not include cogs.*)
    :return:class:`data class`
        Nested data class object containing all keys/entries of the .yml
        as attributes, with values corresponding to the key/entry.
    """
    path = COG_CONFIGS_PATH.format(cog_name)
    configs = read_yml(path)
    if not configs:
        print(f"CONFIG ERROR: '{path}' is an empty .yml file! Passing {cog_name} configs as an empty class.")
        return make_dataclass('Configs', (), frozen=True)
    else:
        return generate_classes(configs)


def get_cog_strings(cog_name):
    """Parses cogs/<cog_name>/strings.yml into a usable data structure.

    :param:cog_name:`str`
        Name of the cog package (do not include cogs.*)
    :return:class:`data class`
        Nested data class object containing all keys/entries of the .yml
        as attributes, with values corresponding to the key/entry.
    """
    path = COG_STRINGS_PATH.format(cog_name)
    strings = read_yml(path)
    if not strings:
        print(f"CONFIG ERROR: '{path}' is an empty .yml file. Passing {cog_name} strings as an empty class...")
        return make_dataclass('Strings', (), frozen=True)
    else:
        return generate_classes(strings)


def get_bot_configs():
    """Parses bot_configs.yml into a usable data structure.
    """
    configs = read_yml(BOT_CONFIGS_PATH)
    return generate_classes(configs)


def get_bot_strings():
    """Parses bot_strings.yml into a usable data structure.
    """
    strings = read_yml(BOT_STRINGS_PATH)
    return generate_classes(strings)


def get(path):
    """Override method to read and parse a .yml file from path
    """
    return generate_classes(read_yml(path))
