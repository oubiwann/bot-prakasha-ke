import os
import time
from datetime import datetime

from twisted.protocols.basic import LineReceiver
from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory

import config

class Publisher(IRCClient):
    nickname = config.irc.nick
    password = config.irc.serverPassword

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

class MessageLogger(object):
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """
        Write a message to the file.
        """
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()

class Logger(IRCClient):
    """
    A logging IRC bot.
    """
    nickname = config.log.nick
    
    def connectionMade(self):
        IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
            time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
            time.asctime(time.localtime(time.time())))
        self.logger.close()

    # callbacks for events
    def signedOn(self):
        """
        Called when bot has succesfully signed on to server.
        """
        self.join(self.factory.channel)

    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """
        This will get called when the bot receives a message.
        """
        user = user.split('!', 1)[0]
        # check to see if they're sending me a private message
        if channel == self.nickname:
            template = "%s on channel %s attempted to send this private message: \n%s"
            print template % (user, channel, msg)
            return
        # log public messages
        self.logger.log("<%s> %s" % (user, msg))
        
    def action(self, user, channel, msg):
        """
        This will get called when the bot sees someone do an action.
        """
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks
    def irc_NICK(self, prefix, params):
        """
        Called when an IRC user changes their nickname.
        """
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

class LoggerFactory(ReconnectingClientFactory):
    """
    A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = Logger
    connection = None

    def __init__(self, server, channel):
        self.channel = channel
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m%B")
        day = now.strftime("%d")
        path = "%s/%s/%s/" % (config.log.http.docRoot, year, month)
        filename = "%s.%s_%s.txt" % (day, server, channel)
        if not os.path.exists(path):
            os.makedirs(path)
        self.filename = path + filename



