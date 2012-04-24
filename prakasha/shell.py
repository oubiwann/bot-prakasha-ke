import base64
from glob import glob
import os
from pprint import pprint
import sys

from twisted.cred import checkers, portal
from twisted.conch import manhole, manhole_ssh
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.python import failure, log

from zope.interface import implements

from prakasha import config
from prakasha import exceptions


def _getKey(path):
    if not os.path.exists(path):
        raise exceptions.MissingSSHServerKeysError()
    with open(path) as keyBlob:
        return Key.fromString(data=keyBlob.read())

def getPrivKey():
    privKeyPath = os.path.join(
        config.ssh.keydir, config.ssh.privkey)
    return _getKey(privKeyPath)


def getPubKey():
    pubKeyPath = os.path.join(
        config.ssh.keydir, config.ssh.pubkey)
    return _getKey(pubKeyPath)


class MOTDColoredManhole(manhole.ColoredManhole):
    """
    """
    ps = (":>> ", "... ")

    def initializeScreen(self):
        manhole.ColoredManhole.initializeScreen(self)
        self.terminal.write(self.getMOTD())

    def getMOTD(self):
        return config.ssh.banner or "Welcome to MOTDColoredManhole!"


class ExecutingTerminalSession(manhole_ssh.TerminalSession):
    """
    """
    def windowChanged(self, coords):
        log.msg("New coordinates: %s" % str(coords))

    def execCommand(self, proto, cmd):
        avatar = proto.session.avatar
        namespace = updateNamespace(proto.session.session.namespace)
        try:
            result = eval(cmd, namespace)
        except NameError:
            command = cmd.split("(")[0]
            msg = "Command '%s' not found in namespace!" % command
            raise exceptions.IllegalAPICommand(msg)
        avatar.conn.transport.loseConnection()


class ExecutingTerminalRealm(manhole_ssh.TerminalRealm):
    """
    """
    sessionFactory = ExecutingTerminalSession

    def __init__(self, namespace):
        self.sessionFactory.namespace = namespace


class CommandAPI(object):

    def __init__(self, loggerFactory, publisher):
        self.loggerFactory = loggerFactory
        self.channels = self.getChannels()
        self.publisher = publisher
        self.namespace = None

    def setNamespace(self, namespace):
        self.namespace = namespace

    def getChannels(self):
        return self.loggerFactory.channels

    def ls(self):
        keys = sorted(self.namespace.keys())
        pprint(keys)

    def banner(self):
        print config.ssh.banner

    def joinAll(self):
        for channel in self.channels:
            self.publisher.join(channel)

    def say(self, channel, message):
        """
        A convenience wrapper for the IRC client method of the same name.
        """
        self.publisher.say(channel, message)

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
        Send a public message to all channels.
        """
        for channel in self.channels:
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
        for channel in self.channels:
            self.setTopic(channel, topic, say)


def updateNamespace(namespace):

    logService = namespace["services"].getServiceNamed(
        config.log.servicename)
    loggerFactory = logService.args[2]

    pubService = namespace["services"].getServiceNamed(
        config.irc.servicename)
    publisher = pubService.args[2].connection

    commands = CommandAPI(loggerFactory, publisher)
    commands.joinAll()
    namespace.update({
        "os": os,
        "sys": sys,
        "config": config,
        "pprint": pprint,
        "ls": commands.ls,
        "banner": commands.banner,
        "channels": commands.getChannels,
        "info": commands.banner,
        "publisher": publisher,
        "say": commands.say,
        "sayMulti": commands.sayMulti,
        "sayAll": commands.sayAll,
        "setTopic": commands.setTopic,
        "setMultiTopics": commands.setMultiTopics,
        "setAllTopics": commands.setAllTopics,
        })
    commands.setNamespace(namespace)
    return namespace


def getShellFactory(**namespace):

    def getManhole(serverProtocol):
        return MOTDColoredManhole(updateNamespace(namespace))

    realm = ExecutingTerminalRealm(namespace)
    realm.chainedProtocolFactory.protocolFactory = getManhole
    sshPortal = portal.Portal(realm)
    factory = manhole_ssh.ConchFactory(sshPortal)
    factory.privateKeys = {'ssh-rsa': getPrivKey()}
    factory.publicKeys = {'ssh-rsa': getPubKey()}
    factory.portal.registerChecker(SSHPublicKeyDatabase())
    return factory
