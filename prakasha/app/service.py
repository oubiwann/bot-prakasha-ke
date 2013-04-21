import sys

from twisted.application import service, internet
from twisted.conch import manhole_ssh
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.cred import portal
from twisted.internet.protocol import ServerFactory
from twisted.internet.ssl import ClientContextFactory
from twisted.python import usage
from twisted.scripts import twistd
from twisted.web import server, static, vhost

from carapace.app.shell import pythonshell
from carapace.sdk import (
    const as carapace_const, scripts as carapace_scripts, registry)
from carapace.util import ssh as carapace_util

from prakasha import exceptions, meta
from prakasha.app import auth, shell
from prakasha.app.api import CommandAPI
from prakasha.app.logger import LoggerFactory
from prakasha.app.publisher import Listener, PublisherFactory
from prakasha.app.shell import ShellTerminalRealm


config = registry.getConfig()


class SubCommandOptions(usage.Options):
    """
    A base class for subcommand options.

    Can also be used directly for subcommands that don't have options.
    """


class Options(usage.Options):
    """
    """
    subCommands = [
        ["keygen", None, SubCommandOptions,
         "Generate ssh keys for the server"],
        ["shell", None, SubCommandOptions, "Login to the server"],
        ["stop", None, SubCommandOptions, "Stop the server"],
        ]

    def parseOptions(self, options):
        usage.Options.parseOptions(self, options)
        # check options
        if self.subCommand == carapace_const.KEYGEN:
            carapace_scripts.KeyGen()
            sys.exit(0)
        elif self.subCommand == carapace_const.SHELL:
            carapace_scripts.ConnectToShell()
            sys.exit(0)
        elif self.subCommand == carapace_const.STOP:
            carapace_scripts.StopDaemon()
            sys.exit(0)


def makeService(options):
    # primary setup
    application = service.Application(meta.display_name)
    services = service.IServiceCollection(application)

    # setup message server
    serverFactory = ServerFactory()
    serverFactory.protocol = Listener
    serverFactory.publisher = PublisherFactory()

    msgServer = internet.TCPServer(config.listener.port, serverFactory)
    msgServer.setName(config.listener.servicename)
    msgServer.setServiceParent(services)

    # setup IRC message client
    if config.irc.sslEnabled:
        msgService = internet.SSLClient(config.irc.server, config.irc.port,
            serverFactory.publisher, ClientContextFactory())
    else:
        msgService = internet.TCPClient(config.irc.server, config.irc.port,
            serverFactory.publisher)
    msgService.setName(config.irc.servicename)
    msgService.setServiceParent(services)

    # setup IRC log client
    logger = LoggerFactory(config.irc.server, config.log.channels)
    logService = internet.TCPClient(config.irc.server, config.irc.port,
        logger)
    logService.setName(config.log.servicename)
    logService.setServiceParent(services)

    # setuplog rotator
    rotService = internet.TimerService(config.log.rotate.checkInterval,
        logger.rotateLogs, logService)
    rotService.setName(config.log.rotate.servicename)
    rotService.setServiceParent(services)

    # setup log file web server
    webroot = static.File(config.log.http.docRoot)
    if config.log.http.vhostEnabled:
        vResource = vhost.VHostMonsterResource()
        webroot.putChild('vhost', vResource)
    if config.log.http.auth == 'basic':
        guarded = auth.guardResourceWithBasicAuth(
            webroot, config.log.http.realm, config.log.http.users)
        site = server.Site(guarded)
    else:
        site = server.Site(webroot)
    webserver = internet.TCPServer(config.log.http.port, site)
    webserver.setName(config.log.http.servicename)
    webserver.setServiceParent(services)

    # setup ssh access to a Python shell
    interpreterType = carapace_const.PYTHON
    sshFactory = getShellFactory(
        interpreterType, app=application, services=services)
    sshserver = internet.TCPServer(config.ssh.port, sshFactory)
    sshserver.setName(config.ssh.servicename)
    sshserver.setServiceParent(services)
    return services


def getShellFactory(interpreterType, **namespace):
    realm = ShellTerminalRealm(namespace, CommandAPI)
    sshPortal = portal.Portal(realm)
    factory = manhole_ssh.ConchFactory(sshPortal)
    factory.privateKeys = {'ssh-rsa': carapace_util.getPrivKey()}
    factory.publicKeys = {'ssh-rsa': carapace_util.getPubKey()}
    factory.portal.registerChecker(SSHPublicKeyDatabase())
    return factory
