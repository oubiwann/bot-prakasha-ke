import os
import time
from datetime import datetime

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ClientFactory

from carapace.sdk import registry


config = registry.getConfig()


def getLogFilename(server, channel):
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m%B")
    day = now.strftime("%d%A")
    path = "%s/%s/%s/%s_%s/" % (config.log.http.docRoot, year, month, server,
        channel)
    filename = "%s.txt" % day
    if not os.path.exists(path):
        os.makedirs(path)
    return path + filename


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
        timestamp = datetime.now().strftime("[%d-%b-%Y %H:%M:%S]")
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LoggerClient(IRCClient):
    """
    A logging IRC Client.
    """
    nickname = config.log.nick
    loggers = {}

    def connectionMade(self):
        IRCClient.connectionMade(self)
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
        for channel in self.getChannels():
            self.join(channel)

    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.loggers[channel].log("[%s (logger bot) has joined %s]" % (
            config.log.nick, channel))
        self.initialTopicLogged = False
        self.topic(channel)

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

    def irc_TOPIC(self, prefix, params):
        """
        Called when an IRC user changes the channel topic.
        """
        user = prefix.split("!")[0]
        channel, new_topic = params
        self.loggers[channel].log("* %s changed the topic to '%s'" % (
            user, new_topic))

    def irc_RPL_TOPIC(self, prefix, params):
        if self.initialTopicLogged:
            return
        nick, channel, topic = params
        self.loggers[channel].log(
            "[Channel topic for %s was set as '%s']" % (channel, topic))
        self.initialTopicLogged = True


class LoggerFactory(ClientFactory):
    """
    A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = LoggerClient
    connection = None
    lastRotation = None
    doRotate = False

    def __init__(self, server, channels):
        self.server = server
        self.channels = channels

    def startFactory(self, *args, **kwds):
        date = datetime.now().timetuple()[0:3]
        rotateDate = datetime(*date+self.getRotateTime())
        print "Setting initial rotation time now ..."
        self.lastRotation = rotateDate
        ClientFactory.startFactory(self, *args, **kwds)

    def getRotateTime(self):
        time = config.log.rotate.time.split(':')
        return tuple([int(x) for x in time])

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
        print "Last rotation: %s" % str(last)
        now = datetime.now()
        diff = now - last
        diffInSeconds = (diff.days * 60 * 60 * 24) + diff.seconds
        elapsedHours = (diffInSeconds) / 60. / 60.
        timeCheck = config.log.rotate.maxAgeHours
        if elapsedHours >= timeCheck:
            print "Elapsed time (%s) is more than %s hours; resetting..." % (
                elapsedHours, timeCheck)
            service.stopService()
            service.startService()
            rotateDate = datetime(*now.timetuple()[0:3]+self.getRotateTime())
            self.lastRotation = rotateDate
        #else:
        #    print "Elapsed time (%s) is not more than %s hours; skipping..." % (
        #        elapsedHours, timeCheck)
