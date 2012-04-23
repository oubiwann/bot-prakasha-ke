from twisted.protocols.basic import LineReceiver
from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory

import config


class Publisher(IRCClient):
    nickname = config.irc.nick
    password = config.irc.serverPassword
    lineRate = config.irc.lineRate

    def connectionMade(self):
        print "Connection made", self.transport
        self.factory.connection = self
        IRCClient.connectionMade(self)

        if self.factory.queued:
            for channel, message in self.factory.queued:
                self.send(channel, message)
        self.factory.queued = []

    def send(self, channel, message):
        self.join(channel)
        self.msg(channel, message)


class PublisherFactory(ReconnectingClientFactory):
    protocol = Publisher
    queued = []
    connection = None


class Listener(LineReceiver):
    """
    This protocol is used for receiving messages via TCP and sending them to
    the appropriate IRC channel on a single IRC server.

    Messages are sent in the following format:

        mypassword:#superchannel:this is the coolest message ever
    """
    def connectionMade(self):
        print "Someone has connected to me! Transport:", self.transport

    def lineReceived(self, line):
        print "Got line: %s" % line
        publisher = self.factory.publisher
        # XXX this is awful for an RPC mechanism :-( do it right!
        command = None
        password = None
        if "::" not in line:
            password, channel, message = line.split(':', 2)
            assert password == config.listener.password
            if publisher.connection:
                print "Sending message:", channel, message
                publisher.connection.send(channel, message)
            else:
                print "Queueing message:", channel, message
                publisher.queued.append((channel, message))
        else:
            command, arg1, arg2 = line.split("::")
            if command == "TOPIC":
                publisher.topic(arg1, topic=arg2)
            elif command == "MULTITOPIC":
                for channel in arg1.split(","):
                    publisher.topic(channel, topic=arg2)
            elif command == "BROADCAST":
                pass
