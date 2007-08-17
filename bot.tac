from twisted.web import vhost
from twisted.web import server
from twisted.web import static
from twisted.application import service
from twisted.internet.protocol import ServerFactory
from twisted.application.internet import TCPServer, TCPClient, SSLClient
from twisted.internet.ssl import ClientContextFactory

import config
from publishbot import Listener
from publishbot import PublisherFactory

application = service.Application("publishbot")
services = service.IServiceCollection(application)

# setup message server
serverFactory = ServerFactory()
serverFactory.protocol = Listener
serverFactory.publisher = PublisherFactory()

msgServer = TCPServer(config.listener.port, serverFactory)
msgServer.setServiceParent(services)

# setup IRC message client
if config.irc.sslEnabled:
    ircservice = SSLClient(config.irc.server, config.irc.port,
        serverFactory.publisher, ClientContextFactory())
else:
    ircservice = TCPClient(config.irc.server, config.irc.port,
        serverFactory.publisher)
ircservice.setServiceParent(services)

# setup web server
webroot = static.File(config.log.http.docRoot)
if config.log.http.vhostEnabled:
    vResource = vhost.VHostMonsterResource()
    webroot.putChild('vhost', vResource)
site = server.Site(webroot)
webserver = TCPServer(config.log.http.port, site)
webserver.setServiceParent(services)
