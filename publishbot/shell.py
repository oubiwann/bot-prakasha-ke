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


def getShellFactory(namespace=None):

    def getManhole(serverProtocol):
        return MOTDColoredManhole(namespace)

    if not namespace:
        from pprint import pprint
        import sys
        namespace = {
            "os": os, 
            "sys": sys, 
            "config": config,
            "pprint": pprint,
            }
    realm = manhole_ssh.TerminalRealm() 
    realm.chainedProtocolFactory.protocolFactory = getManhole

    sshPortal = portal.Portal(realm)
    factory = manhole_ssh.ConchFactory(sshPortal)
    factory.privateKeys = {'ssh-rsa': getPrivKey()}
    factory.publicKeys = {'ssh-rsa': getPubKey()}
    factory.portal.registerChecker(SSHPublicKeyDatabase())
    return factory
