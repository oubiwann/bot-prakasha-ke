# IRC
class IRC(object): pass
irc = IRC()
irc.nick = 'loudmouth'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.sslEnabled = False

# Listener
class Listener(object): pass
listener = Listener()
listener.port = 1234
listener.password = 'ircb0tz'

# Log
class Log(object): pass
class HTTP(object): pass
log = Log()
log.nick = 'nomouth-logger'
#log.nick = 'wallflower'
log.channels = ['#adytum', '#tmlabs', '#divmod-fanclub', '#divmod', '#twisted',
    '#twisted.web', '#storm']
#log.channels = ["#adytum", "#adytum-test"]
log.rotateCheckInterval = 60
log.rotateTime = '00:00'
log.http = HTTP()
log.http.port = 1235
log.http.docRoot = 'irclogs'
log.http.vhostEnabled = True
log.http.vhost= 'localhost'
