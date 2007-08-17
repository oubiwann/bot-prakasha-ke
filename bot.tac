from twisted.internet.protocol import ServerFactory, ReconnectingClientFactory
from twisted.application.internet import TCPServer, TCPClient, SSLClient
from twisted.application.service import Application
from twisted.internet.ssl import ClientContextFactory

from publishbot import Listener, Publisher
import config


application = Application("publishbot")

serverFactory = ServerFactory()
serverFactory.protocol = Listener

clientFactory = ReconnectingClientFactory()
clientFactory.protocol = Publisher
clientFactory.queued = []
clientFactory.connection = None

serverFactory.publisher = clientFactory

server = TCPServer(config.listener.port, serverFactory)
server.setServiceParent(application)
if config.irc.enableSSL:
    ircservice = SSLClient(config.irc.server, config.irc.port,
        clientFactory, ClientContextFactory())
else:
    ircservice = TCPClient(config.irc.server, config.irc.port,
        clientFactory)
ircservice.setServiceParent(application)
