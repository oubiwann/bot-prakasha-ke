import os
import time
from datetime import datetime

from twisted.protocols.basic import LineReceiver
from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.protocol import ClientFactory

import config

def getLogFilename(server, channel):
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%H%M%S_%m%B")
    day = now.strftime("%d")
    path = "%s/%s/%s/" % (config.log.http.docRoot, year, month)
    filename = "%s.%s_%s.txt" % (day, server, channel)
    if not os.path.exists(path):
        os.makedirs(path)
    return path + filename

def rotateLogs(service):
    """

    """
    serviceLogger = service.args[-1]
    print "Last rotation: %s" % str(serviceLogger.lastRotation)
    now = datetime.now()
    #hoursAgo = (now - serviceLogger.lastRotation).seconds /60. /60.
    hoursAgo = (now - serviceLogger.lastRotation).seconds /60.
    #import pdb;pdb.set_trace()
    # XXX hard-coded 24-hour rotation
    #if hoursAgo >= 24:
    if hoursAgo >= 5:
        print "hoursAgo is more than ten (minutes). Resetting..."
        # XXX this causes a looping problem with reconnecting clients
        serviceLogger.stopFactory()
        serviceLogger.startFactory()
        service.stopService()
        service.startService()
        midnight = datetime(*now.timetuple()[0:3])
        t = list(now.timetuple())
        t[4] = t[4] - 2
        midnight = datetime(*t[:-2])
        serviceLogger.lastRotation = midnight
    else:
        print "hoursAgo is not more than ten (minutes). Skipping..."
        

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
    A logging IRC Client.
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

class LoggerFactory(ClientFactory):
    """
    A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = Logger
    connection = None
    lastRotation = None

    def __init__(self, server, channel):
        self.server = server
        self.channel = channel
        self.filename = getLogFilename(self.server, self.channel)
        midnight = datetime(*datetime.now().timetuple()[0:3])
        self.lastRotation = midnight

    def startFactory(self, *args, **kwds):
        self.filename = getLogFilename(self.server, self.channel)
        ClientFactory.startFactory(self, *args, **kwds)

    def clientConnectionLost(self, connector, reason):
        """
        If we get disconnected, reconnect to server.
        """
        print "lost client connection: %s" % str(reason)
        #print "Disconnected from the server; attempting to reconnect ..."
        #connector.connect()
