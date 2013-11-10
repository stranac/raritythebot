import requests
import inspect

from utils import redent

import config


irc_commands = {}
admin_commands = {}
command_help = {}


class irc_command(object):
    """
    Decorator which adds a function to the irc_commands dict.
    Use to make a function a command for the bot.
    """
    def __init__(self, level):
        self.commands = admin_commands if level == 'admin' else irc_commands
        self.level = level

    def __call__(self, f):
        self.commands[f.__name__] = f
        if self.level != 'admin':
            command_help[f.__name__] = inspect.getdoc(f)
        return f


@irc_command('user')
def help(args, bot):
    """
    help: show all available commands.
    help <command>: show help for a single command.
    """
    args = args.strip()
    if not args:
        commands = ', '.join(command_help)
        return ('Available commands: {}. Use {}help <command> to get help '
                'on a specific command.').format(commands, config.trigger)
    return command_help.get(args, 'No help for command: args')


@irc_command('user')
def source(*args):
    """
    Get a link to my source code.
    """
    return 'https://github.com/stranac/raritythebot'

@irc_command('user')
def paste(code, bot):
    """
    Paste a piece of code to http://bpaste.net/
    Use a semicolon to end a line, multiple semicolons to end blocks.
    """
    data = {'code': redent(code),
            'language': 'python',
            'webpage': '',
            'private': 'on'
            }
    r = requests.post('http://bpaste.net/', data)
    return r.url.encode()


@irc_command('admin')
def say_to(args, bot):
    """
    args: <user or channel> <message>
    Send message to the target.
    """
    target, _, msg = args.partition(' ')
    bot.msg(target, msg)

@irc_command('admin')
def join(channel, bot):
    """
    Join channel.
    """
    bot.join(channel)
    return 'Joined %s' % channel
