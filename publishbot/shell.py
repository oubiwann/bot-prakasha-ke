import base64
from glob import glob
import os

from twisted.cred import checkers, portal
from twisted.conch import manhole, manhole_ssh
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.python import failure

from zope.interface import implements

from publishbot import config


def getPrivKey():
    privKeyPath = os.path.join(
        config.ssh.keydir, config.ssh.privkey)
    with open(privKeyPath) as privateKeyBlob:
        privateBlob = privateKeyBlob.read()
        return Key.fromString(data=privateBlob)


def getPubKey():
    pubKeyPath = os.path.join(
        config.ssh.keydir, config.ssh.pubkey)
    with open(pubKeyPath) as publicKeyBlob:
        publicBlob = publicKeyBlob.read()
        return Key.fromString(data=publicBlob)


class MOTDColoredManhole(manhole.ColoredManhole):
    """
    """
    def initializeScreen(self):
        manhole.ColoredManhole.initializeScreen(self)
        self.terminal.write(self.getMOTD())

    def getMOTD(self):
        return config.ssh.banner or "Welcome to MOTDColoredManhole!"


class CommandAPI(object):

    def __init__(self, loggerFactory, publisher):
        self.loggerFactory = loggerFactory
        self.channels = self.loggerFactory.channels
        self.publisher = publisher

    def joinAll(self):
        for channel in self.channels:
            self.publisher.join(channel)

    def broadcast(self, message):
        for channel in self.channels:
            self.publisher.say(channel, message)

    def setTopic(self, channel, topic):
        self.publisher.topic(channel, topic)

    def setAllTopics(self, data):
        for channel, topic in data.items():
            self.setTopic(channel, topic)


def updateNamespace(namespace):

    from pprint import pprint
    import sys

    def banner():
        print config.ssh.banner

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
        "banner": banner,
        "info": banner,
        "publisher": publisher,
        "broadcast": commands.broadcast,
        "setTopic": commands.setTopic,
        "setAllTopics": commands.setAllTopics,
        })
    return namespace


def getShellFactory(**namespace):

    def getManhole(serverProtocol):
        return MOTDColoredManhole(updateNamespace(namespace))

    realm = manhole_ssh.TerminalRealm() 
    realm.chainedProtocolFactory.protocolFactory = getManhole
    sshPortal = portal.Portal(realm)
    factory = manhole_ssh.ConchFactory(sshPortal)
    factory.privateKeys = {'ssh-rsa': getPrivKey()}
    factory.publicKeys = {'ssh-rsa': getPubKey()}
    factory.portal.registerChecker(SSHPublicKeyDatabase())
    return factory
