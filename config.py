# IRC
class Config(object): pass
irc = Config()
irc.nick = 'loudmouth'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.sslEnabled = False

# Listener
listener = Config()
listener.port = 1234
listener.password = 'ircb0tz'

# Log
log = Config()
log.nick = 'nomouth-logger'
#log.nick = 'wallflower'
#log.channels = ['#adytum', '#tmlabs', '#divmod-fanclub', '#divmod', '#twisted',
#    '#twisted.web', '#storm']
log.channels = ["#adytum", "#adytum-test"]
log.rotateCheckInterval = 60
log.rotateTime = '00:00'
log.maxAgeHours = 3
log.http = Config()
log.http.port = 1235
log.http.docRoot = 'irclogs'
log.http.vhostEnabled = True
log.http.vhost= 'localhost'
