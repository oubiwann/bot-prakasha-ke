import os
import time
from datetime import datetime

from twisted.application import internet
from twisted.protocols.basic import LineReceiver
from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.protocol import ClientFactory

import config

def getLogFilename(server, channel):
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m%B")
    #month = now.strftime("%H%M%S_%m%B")
    day = now.strftime("%d")
    path = "%s/%s/%s/%s_%s/" % (config.log.http.docRoot, year, month, server,
        channel)
    filename = "%s.txt" % day
    if not os.path.exists(path):
        os.makedirs(path)
    return path + filename

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
    def __init__(self, filename):
        self.file = open(filename, 'a')

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
    loggers = {}
    
    def connectionMade(self):
        IRCClient.connectionMade(self)
        # XXX hard-coded time
        midnight = datetime(*datetime.now().timetuple()[0:3])
        print "Setting initial rotation time now ..."
        self.factory.lastRotation = midnight
        print self.factory.lastRotation
        for chan in self.getChannels():
            filename = getLogFilename(self.factory.server, chan)
            logger = MessageLogger(filename)
            self.loggers.update({chan: logger})
            logger.log("[connected at %s]" %
                time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        IRCClient.connectionLost(self, reason)
        for logger in self.loggers.values():
            logger.log("[disconnected at %s]" %
                time.asctime(time.localtime(time.time())))
            logger.close()

    def getChannels(self):
        return self.factory.channels

    # callbacks for events
    def signedOn(self):
        """
        Called when bot has succesfully signed on to server.
        """
        #self.join(self.factory.channel)
        for channel in self.getChannels():
            self.join(channel)

    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.loggers[channel].log("[%s (logger bot) has joined %s]" % (
            config.log.nick, channel))

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
        try:
            self.loggers[channel].log("<%s> %s" % (user, msg))
        except KeyError:
            template = "Could not log the following messege to %s:\n%s"
            print template % (channel, msg)
        
    def action(self, user, channel, msg):
        """
        This will get called when the bot sees someone do an action.
        """
        user = user.split('!', 1)[0]
        self.loggers[channel].log("* %s %s" % (user, msg))

    # irc callbacks
    def irc_NICK(self, prefix, params):
        """
        Called when an IRC user changes their nickname.
        """
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        for logger in self.loggers.values():
            logger.log("%s is now known as %s" % (old_nick, new_nick))

#class LoggerFactory(ReconnectingClientFactory):
class LoggerFactory(ClientFactory):
    """
    A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = Logger
    connection = None
    lastRotation = None
    doRotate = False

    def __init__(self, server, channels):
        self.server = server
        self.channels = channels

    def startFactory(self, *args, **kwds):
        midnight = datetime(*datetime.now().timetuple()[0:3])
        self.lastRotation = midnight
        ClientFactory.startFactory(self, *args, **kwds)

    def rotateLogs(self, service):
        """

        """
        if not self.doRotate:
            self.doRotate = True
            return
        last = self.lastRotation
        if not last:
            print "Last rotation is not yet defined; skipping rotation check ..."
            return
        #print "Last rotation: %s" % str(last)
        now = datetime.now()
        hoursAgo = (now - last).seconds /60. /60.
        #hoursAgo = (now - last).seconds /60.
        # XXX hard-coded 24-hour rotation
        timeCheck = 24
        #timeCheck = 5
        if hoursAgo >= timeCheck:
            print "hoursAgo is more than %s; resetting..." % timeCheck
            #print "hoursAgo is more than %s (minutes); resetting..." % timeCheck
            # XXX this causes a looping problem with reconnecting clients
            service.stopService()
            service.startService()
            midnight = datetime(*now.timetuple()[0:3])
            # XXX - test code of a short interval
            #t = list(now.timetuple())
            #t[4] = t[4] - 2
            #midnight = datetime(*t[:-2])
            self.lastRotation = midnight
        #else:
            #print "hoursAgo is not more than %s; skipping..." % timeCheck
            #print "hoursAgo is not more than %s (minutes); skipping..." % timeCheck


