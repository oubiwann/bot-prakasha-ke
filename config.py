# IRC
class IRC(object): pass
irc = IRC()
irc.nick = 'loudmouth'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.enableSSL = False

# Listener
class Listener(object): pass
listener = Listener()
listener.port = 1234
listener.password = 'ircb0tz'
