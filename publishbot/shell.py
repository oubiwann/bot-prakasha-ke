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


def getShellFactory(namespace=None):

    def getManhole(xxx):
        print "!", xxx
        return manhole.Manhole(namespace)

    if not namespace:
        namespace = globals()
    realm = manhole_ssh.TerminalRealm() 
    realm.chainedProtocolFactory.protocolFactory = getManhole

    sshPortal = portal.Portal(realm)
    factory = manhole_ssh.ConchFactory(sshPortal)
    factory.privateKeys = {'ssh-rsa': getPrivKey()}
    factory.publicKeys = {'ssh-rsa': getPubKey()}
    #factory.portal = sshPortal
    factory.portal.registerChecker(SSHPublicKeyDatabase())
    return factory
