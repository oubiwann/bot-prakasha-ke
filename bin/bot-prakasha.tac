from twisted.web import vhost
from twisted.web import server
from twisted.web import static
from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet.ssl import ClientContextFactory

from prakasha import auth, config, shell
from prakasha.logger import LoggerFactory
from prakasha.publisher import Listener, PublisherFactory


application = service.Application("prakasha")
services = service.IServiceCollection(application)

# XXX move these services into prakasha.services
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
    guarded = auth.guardResourceWithBasicAuth(webroot, config.log.http.realm,
        config.log.http.users)
    site = server.Site(guarded)
else:
    site = server.Site(webroot)
webserver = internet.TCPServer(config.log.http.port, site)
webserver.setName(config.log.http.servicename)
webserver.setServiceParent(services)


# setup ssh access to a Python shell
sshFactory = shell.getShellFactory(app=application, services=services)
sshserver = internet.TCPServer(config.ssh.port, sshFactory)
sshserver.setName(config.ssh.servicename)
sshserver.setServiceParent(services)
