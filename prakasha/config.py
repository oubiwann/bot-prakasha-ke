# IRC
class Config(object): pass
irc = Config()
irc.servicename = "IRC Client"
irc.nick = 'prakasha-bot'
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
ssh.keydir = ".prakasha-ssh"
ssh.privkey = "id_rsa"
ssh.pubkey = "id_rsa.pub"
ssh.localdir = "~/.ssh"
ssh.banner = """

Welcome to

     .;@@
       .@@@
         @@@                                 +'
         '@@;                                +@@`
       ::,@@@::::::::::::::::::::::::::::::::#@@::::::::,
       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
          @@@                       @@@      +@@`
          @@@    '#+,        `#@@@#,@@@      +@@`
          @@@ .@@@@@@@+    `@@@@@'.`:@@      +@@`
          @@@@.    .@@@@  .@@@@       @@     +@@`
          @@@        ;@@` @@@'        `@@    +@@`
          @@@@`       `@  +@`        `@@@    +@@`   @
          @@@@@:      @    #,       '@@@'    +@@`   @@@
          @@#+@@@.   @      `+   `#@@@@+      @@.  ,@@.
          #@#  @@@@@          `#@@@@@#         @@'#@#

                        __            __          __
         ___  _______ _/ /_____ ____ / /  ___ _  / /_____
        / _ \/ __/ _ `/  '_/ _ `(_-</ _ \/ _ `/ /  '_/ -_)
       / .__/_/  \_,_/_/\_\\\\_,_/___/_//_/\_,_/ /_/\_\\\\__/
      /_/

You are in the prakasha interactive Python shell.
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
log.nick = 'prakasha-log'
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
log.http.realm = 'bot-prakasha-ke IRC Logs'

# Log web server users
log.http.users = {
    'Jojo': 'c1rcu5b0y',
    }
log.http.userdb = "httpd.password"
