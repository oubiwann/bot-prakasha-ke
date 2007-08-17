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

# Log
class Log(object): pass
class HTTP(object): pass
log = Log()
log.nick = 'loudmouth-logger'
log.channels = ['#adytum', '#tmlabs', '#divmod-fanclub', '#divmod', '#twisted',
    '#twisted.web']
log.channels = ['#adytum']
log.http = HTTP()
log.http.port = 1235
log.http.docRoot = 'irclogs'
log.http.vhostEnabled = True
