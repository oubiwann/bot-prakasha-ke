from ConfigParser import SafeConfigParser
import json
import os

from zope.interface import moduleProvides

from carapace.config import Config, Configurator, main, ssh
from carapace.sdk import interfaces


moduleProvides(interfaces.IConfig)


# Main
main.config.userdir = os.path.expanduser("~/.prakasha-bot")
main.config.userfile = "%s/%s" % (main.config.userdir, main.config.localfile)

# Internal SSH Server
ssh.servicename = "SSH Server"
ssh.port = 6622
ssh.keydir = ".prakasha-ssh"
ssh.banner = """:
: Welcome to
:
:    .;@@
:      .@@@
:        @@@                                 +'
:        '@@;                                +@@`
:      ::,@@@::::::::::::::::::::::::::::::::#@@::::::::,
:      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
:         @@@                       @@@      +@@`
:         @@@    '#+,        `#@@@#,@@@      +@@`
:         @@@ .@@@@@@@+    `@@@@@'.`:@@      +@@`
:         @@@@.    .@@@@  .@@@@       @@     +@@`
:         @@@        ;@@` @@@'        `@@    +@@`
:         @@@@`       `@  +@`        `@@@    +@@`   @
:         @@@@@:      @    #,       '@@@'    +@@`   @@@
:         @@#+@@@.   @      `+   `#@@@@+      @@.  ,@@.
:         #@#  @@@@@          `#@@@@@#         @@'#@#
:
:                       __            __          __
:        ___  _______ _/ /_____ ____ / /  ___ _  / /_____
:       / _ \/ __/ _ `/  '_/ _ `(_-</ _ \/ _ `/ /  '_/ -_)
:      / .__/_/  \_,_/_/\_\\\\_,_/___/_//_/\_,_/ /_/\_\\\\__/
:     /_/
:
: You are in the prakasha interactive Python shell.
: Type 'dir()' to see the objects in the current namespace.
:
: Enjoy!
:
"""

# IRC
irc = Config()
irc.servicename = "IRC Client"
irc.nick = 'prakasha-bot'
irc.server = 'irc.freenode.net'
irc.port = 6667
irc.serverPassword = None
irc.sslEnabled = False
irc.lineRate = 1

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
log.channels = ["#adytum", "#uls"]

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
log.http.vhost = 'localhost'
#log.http.auth = 'basic'
log.http.auth = None
log.http.realm = 'bot-prakasha-ke IRC Logs'

# Log web server users
log.http.users = {
    'Jojo': 'c1rcu5b0y',
    }
log.http.userdb = "httpd.password"


class PrakashaConfigurator(Configurator):

    def __init__(self, main, ssh, irc, listener, log):
        super(PrakashaConfigurator, self).__init__(main, ssh)
        self.irc = irc
        self.listener = listener
        self.log = log

    def buildDefaults(self):
        config = super(PrakashaConfigurator, self).buildDefaults()
        config.add_section("IRC")
        config.set("IRC", "servicename", self.irc.servicename)
        config.set("IRC", "nick", self.irc.nick)
        config.set("IRC", "server", self.irc.server)
        config.set("IRC", "port", str(self.irc.port))
        config.set("IRC", "serverPassword", self.irc.serverPassword or "")
        config.set("IRC", "sslEnabled", str(self.irc.sslEnabled))
        config.set("IRC", "lineRate", str(self.irc.lineRate))

        config.add_section("Listener")
        config.set("Listener", "servicename", self.listener.servicename)
        config.set("Listener", "host", self.listener.host)
        config.set("Listener", "port", str(self.listener.port))
        config.set("Listener", "password", self.listener.password)

        config.add_section("Logger")
        config.set("Logger", "servicename", self.log.servicename)
        config.set("Logger", "nick", self.log.nick)
        config.set("Logger", "channels", json.dumps(self.log.channels))

        config.add_section("Rotator")
        config.set("Rotator", "servicename", self.log.rotate.servicename)
        config.set(
            "Rotator", "checkInterval", str(self.log.rotate.checkInterval))
        config.set("Rotator", "time", self.log.rotate.time)
        config.set("Rotator", "maxAgeHours", str(self.log.rotate.maxAgeHours))

        config.add_section("HTTP")
        config.set("HTTP", "servicename", self.log.http.servicename)
        config.set("HTTP", "port", str(self.log.http.port))
        config.set("HTTP", "docRoot", self.log.http.docRoot)
        config.set("HTTP", "vhostEnabled", str(self.log.http.vhostEnabled))
        config.set("HTTP", "vhost", self.log.http.vhost)
        config.set("HTTP", "auth", str(self.log.http.auth))
        config.set("HTTP", "realm", self.log.http.realm)
        config.set("HTTP", "users", json.dumps(self.log.http.users))
        config.set("HTTP", "userdb", self.log.http.userdb)
        return config

    def updateConfig(self):
        config = super(PrakashaConfigurator, self).updateConfig()
        irc = self.irc
        listener = self.listener
        log = self.log
        http = self.log.http
        rotate = self.log.rotate

        # IRC
        irc.servicename = config.get("IRC", "servicename")
        irc.nick = str(config.get("IRC", "nick"))
        irc.server = str(config.get("IRC", "server"))
        irc.port = int(config.get("IRC", "port"))
        irc.serverPassword = config.get("IRC", "serverPassword") or None
        sslEnabled = config.get("IRC", "sslEnabled")
        if sslEnabled.lower() == "true":
            sslEnabled = True
        else:
            sslEnabled = False
        irc.sslEnabled = sslEnabled
        irc.lineRate = int(config.get("IRC", "lineRate"))

        # Listener
        listener.servicename = config.get("Listener", "servicename")
        listener.host = config.get("Listener", "host")
        listener.port = int(config.get("Listener", "port"))
        listener.password = config.get("Listener", "password")

        # Log
        log.servicename = config.get("Logger", "servicename")
        log.nick = str(config.get("Logger", "nick"))
        log.channels = [str(x) for x in
                        json.loads(config.get("Logger", "channels"))]

        # Log rotator
        rotate.servicename = config.get("Rotator", "servicename")
        rotate.checkInterval = int(config.get("Rotator", "checkInterval"))
        rotate.time = config.get("Rotator", "time")
        rotate.maxAgeHours = int(config.get("Rotator", "maxAgeHours"))

        # Log web server
        http.servicename = config.get("HTTP", "servicename")
        http.port = int(config.get("HTTP", "port"))
        http.docRoot = config.get("HTTP", "docRoot")
        http.vhostEnabled = bool(config.get("HTTP", "vhostEnabled"))
        http.vhost = config.get("HTTP", "vhost")
        http.auth = config.get("HTTP", "auth")
        http.realm = config.get("HTTP", "realm")

        # Log web server users
        http.users = json.loads(config.get("HTTP", "users"))
        http.userdb = config.get("HTTP", "userdb")

        return config


def updateConfig():
    configurator = PrakashaConfigurator(main, ssh, irc, listener, log)
    configurator.updateConfig()
