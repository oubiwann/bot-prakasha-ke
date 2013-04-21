import os
from pprint import pprint
import sys

from carapace.app.shell import base as baseshell, pythonshell
from carapace.sdk import registry

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


class SessionForTerminalUser(object):
    """
    """
    def __init__(self, avatar):
        self.avatar = avatar
