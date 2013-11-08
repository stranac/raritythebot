"""
Rarity the pony as an irc bot.

Based on habnabit's twisted bot example:
https://gist.github.com/habnabit/5823693
"""

import sys

from twisted.internet import defer, endpoints, protocol, reactor, task
from twisted.python import log
from twisted.words.protocols import irc

from commands import irc_commands, admin_commands
import config


class RarityIRCProtocol(irc.IRCClient):
    nickname = 'RarityThePony'

    def __init__(self):
        self.deferred = defer.Deferred()
        self.admins = set()

    def connectionLost(self, reason):
        self.deferred.errback(reason)

    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
        log.msg('Joined all channels')


    def privmsg(self, user, channel, message):
        nick, _, host = user.partition('!')
        message = message.strip()

        # not a trigger command
        if not message.startswith(config.trigger):
            return

        command, sep, rest = message.lstrip(config.trigger).partition(' ')
        # handle admin login
        if command == 'login':
            self._login(nick, rest)
            return

        # get the function
        if nick in self.admins and command in admin_commands:
            func = admin_commands[command]
        else:
            func = irc_commands.get(command)
            # if there was no function, ignore the message.
            if func is None:
                return

        d = defer.maybeDeferred(func, rest)
        d.addErrback(self._showError)
        d.addCallback(self._sendMessage, channel)


    def _sendMessage(self, msg, target):
        """
        'message >> target' sends message to target.

        If no redirection is present, send the message to
        wherever the command was received from.
        """
        if ' >> ' in msg:
            msg, _, target = msg.partition(' >> ')
        print msg, target
        self.msg(target, msg)

    def _showError(self, failure):
        return failure.getErrorMessage()

    def _login(self, user, password):
        if config.ADMINS.get(user) == password:
            self.admins.add(user)

    def userLeft(self, nick, whatever):
        if nick in self.admins:
            self.admins.remove(nick)
    userQuit = userLeft


class RarityIRCFactory(protocol.ReconnectingClientFactory):
    channels = ['##testing-rarity-36512736712618746', '#python-forum']

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def buildProtocol(self, addr):
        p = RarityIRCProtocol()
        p.factory = self
        return p



def main(reactor, description):
    endpoint = endpoints.clientFromString(reactor, description)
    factory = RarityIRCFactory()
    d = endpoint.connect(factory)
    d.addCallback(lambda protocol: protocol.deferred)
    return d


if __name__ == '__main__':
    log.startLogging(sys.stderr)
    task.react(main, ['tcp:irc.freenode.net:6667'])
