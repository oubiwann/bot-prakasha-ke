import os
from pprint import pprint
import sys

from zope import interface

from twisted.conch import interfaces, manhole_ssh, unix
from twisted.conch.ssh import filetransfer, session
from twisted.python import components

from dreamssh.app.shell import base as baseshell, pythonshell
from dreamssh.sdk import registry

from prakasha.app import api


config = registry.getConfig()


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
            "loggedChannels": self.handler.commandAPI.getLoggedChannels,
            "joinedChannels": self.handler.commandAPI.getJoinedChannels,
            "users": self.handler.commandAPI.getUsers,
            "publisher": self.handler.commandAPI.publisher,
            "say": self.handler.commandAPI.say,
            "sayMulti": self.handler.commandAPI.sayMulti,
            "sayAll": self.handler.commandAPI.sayAll,
            "setTopic": self.handler.commandAPI.setTopic,
            "setMultiTopics": self.handler.commandAPI.setMultiTopics,
            "setAllTopics": self.handler.commandAPI.setAllTopics,
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
    def __init__(self, namespace, apiClass):
        baseshell.ExecutingTerminalRealm.__init__(self, namespace)
        if not apiClass:
            apiClass = api.CommandAPI

        def getManhole(serverProtocol):
            logService = namespace["services"].getServiceNamed(
                config.log.servicename)
            loggerFactory = logService.args[2]

            pubService = namespace["services"].getServiceNamed(
                config.irc.servicename)
            publisher = pubService.args[2].connection
            apis = apiClass(loggerFactory, publisher)
            return self.manholeFactory(apis, namespace)

        self.chainedProtocolFactory.protocolFactory = getManhole


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
