# IRC
class Config(object): pass
irc = Config()
irc.nick = 'loudmouth'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.sslEnabled = False
irc.lineRate = 1

# Internal SSH Server
ssh = Config()
ssh.port = 6622
ssh.username = "root"
ssh.keydir = ".publishbot-ssh"
ssh.privkey = "id_rsa"
ssh.pubkey = "id_rsa.pub"
ssh.localdir = "~/.ssh"

# Listener
listener = Config()
listener.host = "127.0.0.1"
listener.port = 6666
listener.password = 'ircb0tz'

# Log
log = Config()
log.nick = 'publishbot'
log.channels = ["#adytum", "#adytum-test"]
log.rotateCheckInterval = 60
log.rotateTime = '00:00'
log.maxAgeHours = 24

# Log web server
log.http = Config()
log.http.port = 6680
log.http.docRoot = 'irclogs'
log.http.vhostEnabled = True
log.http.vhost= 'localhost'
#log.http.auth = 'basic'
log.http.auth = None
log.http.realm = 'Adytum IRC Logs'

# Log web server users
log.http.users = {
    'Jojo': 'c1rcu5b0y',
    }
log.http.userdb = "httpd.password"
