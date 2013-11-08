irc_commands = {}
admin_commands = {}


class irc_command(object):
    """
    Decorator which adds a function to the irc_commands dict.
    Use to make a function a command for the bot.
    """
    def __init__(self, level):
        self.commands = admin_commands if level == 'admin' else irc_commands

    def __call__(self, f):
        self.commands[f.__name__] = f
        return f


@irc_command('user')
def help(args):
    return '%source: get link to my source code'

@irc_command('user')
def source(args):
    return 'https://github.com/stranac/raritythebot'


@irc_command('admin')
def say_to(args):
    target, _, msg = args.partition(' ')
    return '%s >> %s' % (msg, target)
