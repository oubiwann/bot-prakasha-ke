from pprint import pprint

from carapace.app.shell import base as pythonshell
from carapace.sdk import registry


config = registry.getConfig()


class CommandAPI(pythonshell.CommandAPI):

    def __init__(self, loggerFactory, publisher):
        super(CommandAPI, self).__init__()
        self.loggerFactory = loggerFactory
        self.publisher = publisher
        self.namespace = None

    def getLoggedChannels(self):
        """
        Get the channels that are being logged.
        """
        return self.loggerFactory.channels

    def getJoinedChannels(self):
        """
        Get the channels to which this client has actually joined.
        """
        return self.publisher.userData.keys()

    def getUsers(self, channel):
        """
        For a given channel, get the users that have joined it.
        """
        return self.publisher.getUsers(channel)

    def ls(self):
        """
        List the objects in the current namespace, in alphabetical order.
        """
        keys = sorted(self.namespace.keys())
        pprint(keys)

    def banner(self):
        """
        Display the login banner and associated help or info.
        """
        print config.ssh.banner

    def joinAll(self):
        """
        Join all the channels to which this client is configured to have
        access.
        """
        for channel in self.getLoggedChannels():
            self.publisher.join(channel)

    def say(self, channel, message):
        """
        A convenience wrapper for the IRC client method of the same name.
        """
        self.publisher.send(channel, message)

    def sayMulti(self, data, broadcastMessage=""):
        """
        Send a public message to multipl channels. The 'data' parameter is a
        dict with the keys being the channel names and the values being the
        message to say on that channel. If a 'broadcastMessage' is supplied,
        the values in the dict are ignored, and all channels will used the
        broadcast message.
        """
        for channel, message in data.items():
            if broadcastMessage:
                message = broadcastMessage
            self.say(channel, message)

    def sayAll(self, message):
        """
        Send a public message to all logged channels.
        """
        for channel in self.getLoggedChannels():
            self.say(channel, message)

    def setTopic(self, channel, topic, say=False):
        """
        Set a channel's topic.
        """
        self.publisher.topic(channel, topic)
        if say:
            msg = "Channel topic change: %s" % topic
            self.say(channel, msg)

    def setMultiTopics(self, data, say=False):
        """
        Set the topic for multiple channels at once. The 'data' parameter is a
        dict with the keys being the channel names and the values being the
        desired channel topic. If the 'say' parameter is defined, the new topic
        will also be sent as a public message on the channel.
        """
        for channel, topic in data.items():
            self.setTopic(channel, topic, say)

    def setAllTopics(self, topic, say=False):
        """
        Set the topic for all defined channels at once.  If the 'say' parameter
        is defined, the new topic will also be sent as a public message on the
        channel.
        """
        for channel in self.getLoggedChannels():
            self.setTopic(channel, topic, say)
