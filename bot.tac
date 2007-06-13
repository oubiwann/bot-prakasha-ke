from twisted.internet.protocol import ServerFactory, ReconnectingClientFactory
from twisted.application.internet import TCPServer, TCPClient, SSLClient
from twisted.application.service import Application
from twisted.internet.ssl import ClientContextFactory

from publishbot import Listener, Publisher
import config


application = Application("publishbot")

sf = ServerFactory()
sf.protocol = Listener

cf = ReconnectingClientFactory()
cf.protocol = Publisher
cf.queued = []
cf.connection = None

sf.publisher = cf

TCPServer(config.LISTENER_PORT, sf).setServiceParent(application)
if config.SSL_IRC:
    ircservice = SSLClient(config.IRC_SERVER, config.IRC_PORT, cf,
                           ClientContextFactory())
else:
    ircservice = TCPClient(config.IRC_SERVER, config.IRC_PORT, cf)

ircservice.setServiceParent(application)
