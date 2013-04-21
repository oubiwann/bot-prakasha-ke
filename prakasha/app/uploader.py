import os

from zope import interface

from twisted.conch import interfaces, manhole_ssh, unix
from twisted.conch.ssh import filetransfer, session
from twisted.python import components

from carapace.sdk import registry

from prakasha.app import shell


config = registry.getConfig()


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
    shell.SessionForTerminalUser, SFTPEnabledTerminalUser,
    session.ISession)
