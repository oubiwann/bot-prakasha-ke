import base64
from glob import glob
import os
from pprint import pprint
import sys

from zope import interface

from twisted.cred import checkers, portal
from twisted.conch import interfaces, manhole, manhole_ssh, unix
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import filetransfer, session
from twisted.conch.ssh.channel import SSHChannel
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.python import components, failure, log

from dreamssh.app.shell import pythonshell
from dreamssh.sdk import registry

from prakasha import exceptions


config = registry.getConfig()


class CommandAPI(pythonshell.CommandAPI):

    def __init__(self, loggerFactory, publisher):
        super(CommandAPI, self).__init__()
        self.loggerFactory = loggerFactory
        self.channels = self.getChannels()
        self.publisher = publisher
        self.namespace = None

    def getChannels(self):
        """
        Get the channels to which this client is joined.
        """
        return self.loggerFactory.channels

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


class ShellInterpreter(pythonshell.PythonInterpreter):
    """
    """
    # XXX namespace code needs to be better organized:
    #   * should the CommandAPI be in this module? 
    def updateNamespace(self, namespace={}):
        if not self.handler.commandAPI.appOrig:
            self.handler.commandAPI.appOrig = self.handler.namespace.get("app")
        namespace.update({
            "os": os,
            "sys": sys,
            "pprint": pprint,
            "app": self.handler.commandAPI.getAppData,
            "banner": self.handler.commandAPI.banner,
            "info": self.handler.commandAPI.banner,
            "ls": self.handler.commandAPI.ls,
            "clear": self.handler.commandAPI.clear,
            "quit": self.handler.commandAPI.quit,
            "exit": self.handler.commandAPI.quit,
            "channels": commands.getChannels,
            "users": commands.getUsers,
            "publisher": publisher,
            "say": commands.say,
            "sayMulti": commands.sayMulti,
            "sayAll": commands.sayAll,
            "setTopic": commands.setTopic,
            "setMultiTopics": commands.setMultiTopics,
            "setAllTopics": commands.setAllTopics,
            })
        if "config" not in namespace.keys():
            namespace["config"] = config
        self.handler.namespace.update(namespace)


class ShellManhole(pythonshell.PythonManhole):
    """
    """
    def setInterpreter(self):
        self.interpreter = ShellInterpreter(self, locals=self.namespace)


class ShellTerminalRealm(pythonshell.PythonTerminalRealm):
    """
    """
    manholeFactory = ShellManhole

        
class SFTPEnabledTerminalUser(manhole_ssh.TerminalUser, unix.UnixConchUser):
    """
    """
    def __init__(self, original, avatarId):
        manhole_ssh.TerminalUser.__init__(self, original, avatarId)
        unix.UnixConchUser.__init__(self, avatarId)

    def _runAsUser(self, f, *args, **kw):
        euid = os.geteuid()
        egid = os.getegid()
        groups = os.getgroups()[:16]
        uid, gid = self.getUserGroupId()
        os.setegid(0)
        os.seteuid(0)
        os.setgroups(self.getOtherGroups())
        os.setegid(gid)
        os.seteuid(uid)
        try:
            f = iter(f)
        except TypeError:
            f = [(f, args, kw)]
        try:
            for i in f:
                func = i[0]
                args = len(i)>1 and i[1] or ()
                kw = len(i)>2 and i[2] or {}
                r = func(*args, **kw)
        finally:
            os.setegid(0)
            os.seteuid(0)
            os.setgroups(groups)
            os.setegid(egid)
            os.seteuid(euid)
        return r


class SessionForTerminalUser(object):
    """
    """

    def __init__(self, avatar):
        self.avatar = avatar


class MemorySFTPFile(object):
    """
    """
    interface.implements(interfaces.ISFTPFile)

    def __init__(self, server, filename, flags, attrs):
        self.server = server
        self.filename = filename

    def close(self):
        pass

    def readChunk(self, offset, length):
        pass

    def writeChunk(self, offset, data):
        pass


class MemorySFTPDirectory(object):
    """
    """
    def __init__(self, server, directory):
        self.server = server
        self.files = ['a', 'b']
        self.dir = directory

    def __iter__(self):
        return self

    def next(self):
        try:
           f = self.files.pop(0)
        except IndexError:
            raise StopIteration
        else:
            return (f, "c", {})

    def close(self):
        self.files = []


class ModifiedSFTPServer(unix.SFTPServerForUnixConchUser):
    """
    """
    def openFile(self, filename, flags, attrs):
        return MemorySFTPFile(self, self._absPath(filename), flags, attrs)

    def openDirectory(self, path):
        return MemorySFTPDirectory(self, self._absPath(path))


components.registerAdapter(
    ModifiedSFTPServer, SFTPEnabledTerminalUser,
    filetransfer.ISFTPServer)


components.registerAdapter(
    SessionForTerminalUser, SFTPEnabledTerminalUser,
    session.ISession)
