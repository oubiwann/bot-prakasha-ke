from twisted.internet.protocol import ServerFactory
from twisted.application.internet import TCPServer, TCPClient, SSLClient
from twisted.application.service import Application
from twisted.internet.ssl import ClientContextFactory

import config
from publishbot import Listener
from publishbot import PublisherFactory

application = Application("publishbot")

serverFactory = ServerFactory()
serverFactory.protocol = Listener
serverFactory.publisher = PublisherFactory()

server = TCPServer(config.listener.port, serverFactory)
server.setServiceParent(application)
if config.irc.enableSSL:
    ircservice = SSLClient(config.irc.server, config.irc.port,
        serverFactory.publisher, ClientContextFactory())
else:
    ircservice = TCPClient(config.irc.server, config.irc.port,
        serverFactory.publisher)
ircservice.setServiceParent(application)
