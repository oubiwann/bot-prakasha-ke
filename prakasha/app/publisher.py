from twisted.protocols.basic import LineReceiver
from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory

from dreamssh.sdk import registry


config = registry.getConfig()


class PublisherClient(IRCClient):
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
        self.userData = {}

    def send(self, channel, message):
        if channel not in self.userData.keys():
            self.join(channel)
        self.msg(channel, message)

    def getUsers(self, channel):
        return self.userData[channel]

    def irc_RPL_NAMREPLY(self, network, name_data):
        me, ignore, channel, users = name_data
        users = users.split()
        self.userData[channel] = users

    def irc_ERR_ERRONEUSNICKNAME(self, *args, **kwargs):
        print "irc_ERR_ERRONEUSNICKNAME", args, kwargs

    def irc_ERR_NICKNAMEINUSE(self, *args, **kwargs):
        print "irc_ERR_NICKNAMEINUSE", args, kwargs

    def irc_ERR_PASSWDMISMATCH(self, *args, **kwargs):
        print "irc_ERR_PASSWDMISMATCH", args, kwargs

    def irc_NOTICE(self, *args, **kwargs):
        print "irc_NOTICE", args, kwargs

    def irc_PRIVMSG(self, *args, **kwargs):
        print "irc_PRIVMSG", args, kwargs

    def irc_PRIVMSG(self, *args, **kwargs):
        print "irc_PRIVMSG", args, kwargs

    def irc_ERR_CANNOTSENDTOCHAN(self, *args, **kwargs):
        print "irc_ERR_CANNOTSENDTOCHAN", args, kwargs

    def irc_unknown(self, prefix, command, params):
        print "irc_unknown", prefix, command, params


class PublisherFactory(ReconnectingClientFactory):
    protocol = PublisherClient
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
