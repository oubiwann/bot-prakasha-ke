from twisted.web import vhost
from twisted.web import server
from twisted.web import static
from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet.ssl import ClientContextFactory

import config
from publishbot import Listener
from publishbot import LoggerFactory
from publishbot import PublisherFactory

application = service.Application("publishbot")
services = service.IServiceCollection(application)

# setup message server
serverFactory = ServerFactory()
serverFactory.protocol = Listener
serverFactory.publisher = PublisherFactory()

msgServer = internet.TCPServer(config.listener.port, serverFactory)
msgServer.setServiceParent(services)

# setup IRC message client
if config.irc.sslEnabled:
    msgService = internet.SSLClient(config.irc.server, config.irc.port,
        serverFactory.publisher, ClientContextFactory())
else:
    msgService = internet.TCPClient(config.irc.server, config.irc.port,
        serverFactory.publisher)
msgService.setServiceParent(services)

# setup IRC log clients and log rotators
logger = LoggerFactory(config.irc.server, config.log.channels)
logService = internet.TCPClient(config.irc.server, config.irc.port,
    logger)
logService.setName('logService')
logService.setServiceParent(services)
rotService = internet.TimerService(config.log.rotateCheckInterval,
    logger.rotateLogs, logService)
rotService.setServiceParent(services)

# setup web server
webroot = static.File(config.log.http.docRoot)
if config.log.http.vhostEnabled:
    vResource = vhost.VHostMonsterResource()
    webroot.putChild('vhost', vResource)
site = server.Site(webroot)
webserver = internet.TCPServer(config.log.http.port, site)
webserver.setServiceParent(services)
