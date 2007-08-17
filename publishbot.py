from twisted.words.protocols.irc import IRCClient
from twisted.protocols.basic import LineReceiver

import config

class Publisher(IRCClient):
    nickname = config.irc.nick
    password = config.irc.serverPassword

    def connectionMade(self):
        print "connection made to!", self.transport
        self.factory.connection = self
        IRCClient.connectionMade(self)

        if self.factory.queued:
            for channel, message in self.factory.queued:
                self.send(channel, message)
        self.factory.queued = []

    def send(self, channel, message):
        self.join(channel)
        self.msg(channel, message)

class Listener(LineReceiver):
    """
    This protocol is used for receiving messages via TCP and sending them to
    the appropriate IRC channel on a single IRC server.

    Messages are sent in the following format:

        mypassword:#superchannel:this is the coolest message ever
    """
    def connectionMade(self):
        print "Connection made:", self.transport

    def lineReceived(self, line):
        password, channel, message = line.split(':', 2)
        assert password == config.listener.password
        if self.factory.publisher.connection:
            print "Sending message:", channel, message
            self.factory.publisher.connection.send(channel, message)
        else:
            print "Queueing message:", channel, message
            self.factory.publisher.queued.append((channel, message))
