# IRC
class Config(object): pass
irc = Config()
irc.servicename = "IRC Client"
irc.nick = 'vox-publishbot'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.sslEnabled = False
irc.lineRate = 1

# Internal SSH Server
ssh = Config()
ssh.servicename = "SSH Server"
ssh.port = 6622
ssh.username = "root"
ssh.keydir = ".publishbot-ssh"
ssh.privkey = "id_rsa"
ssh.pubkey = "id_rsa.pub"
ssh.localdir = "~/.ssh"
ssh.banner = """

Welcome to
      ____        _     _ _     _     _           _   
     |  _ \ _   _| |__ | (_)___| |__ | |__   ___ | |_ 
     | |_) | | | | '_ \| | / __| '_ \| '_ \ / _ \| __|
     |  __/| |_| | |_) | | \__ \ | | | |_) | (_) | |_ 
     |_|    \__,_|_.__/|_|_|___/_| |_|_.__/ \___/ \__|

You are in the publishbot interactive Python shell.
Type 'dir()' to see the objects in the current namespace.

Enjoy!
"""

# Listener
listener = Config()
listener.servicename = "Message Service"
listener.host = "127.0.0.1"
listener.port = 6666
listener.password = 'ircb0tz'

# Log
log = Config()
log.servicename = "Logger Service"
log.nick = 'publishbot'
log.channels = ["#adytum", "#adytum-test"]

# Log rotator
log.rotate = Config()
log.rotate.servicename = "Log Rotator Service"
log.rotate.checkInterval = 60
log.rotate.time = '00:00'
log.rotate.maxAgeHours = 24

# Log web server
log.http = Config()
log.http.servicename = "Log Browser"
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
