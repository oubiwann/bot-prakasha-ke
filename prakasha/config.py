from ConfigParser import SafeConfigParser
import json
import os


class Config(object): pass


# Main
main = Config()
main.config = Config()
main.config.userdir = os.path.expanduser("~/.prakasha-bot")
main.config.localfile = "config.ini"
main.config.userfile = "%s/%s" % (main.config.userdir, main.config.localfile)

# IRC
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
log.http.vhost= 'localhost'
#log.http.auth = 'basic'
log.http.auth = None
log.http.realm = 'bot-prakasha-ke IRC Logs'

# Log web server users
log.http.users = {
    'Jojo': 'c1rcu5b0y',
    }
log.http.userdb = "httpd.password"

def buildDefaults():
    config = SafeConfigParser()
    config.add_section("IRC")
    config.set("IRC", "servicename", irc.servicename)
    config.set("IRC", "nick", irc.nick)
    config.set("IRC", "server", irc.server)
    config.set("IRC", "port", str(irc.port))
    config.set("IRC", "serverPassword", irc.serverPassword or "")
    config.set("IRC", "sslEnabled", str(irc.sslEnabled))
    config.set("IRC", "lineRate", str(irc.lineRate))

    config.add_section("SSH")
    config.set("SSH", "servicename", ssh.servicename)
    config.set("SSH", "port", str(ssh.port))
    config.set("SSH", "username", ssh.username)
    config.set("SSH", "keydir", ssh.keydir)
    config.set("SSH", "privkey", ssh.privkey)
    config.set("SSH", "pubkey", ssh.pubkey)
    config.set("SSH", "localdir", ssh.localdir)
    config.set("SSH", "banner", ssh.banner)

    config.add_section("Listener")
    config.set("Listener", "servicename", listener.servicename)
    config.set("Listener", "host", listener.host)
    config.set("Listener", "port", str(listener.port))
    config.set("Listener", "password", listener.password)

    config.add_section("Logger")
    config.set("Logger", "servicename", log.servicename)
    config.set("Logger", "nick", log.nick)
    config.set("Logger", "channels", json.dumps(log.channels))

    config.add_section("Rotator")
    config.set("Rotator", "servicename", log.rotate.servicename)
    config.set("Rotator", "checkInterval", str(log.rotate.checkInterval))
    config.set("Rotator", "time", log.rotate.time)
    config.set("Rotator", "maxAgeHours", str(log.rotate.maxAgeHours))

    config.add_section("HTTP")
    config.set("HTTP", "servicename", log.http.servicename)
    config.set("HTTP", "port", str(log.http.port))
    config.set("HTTP", "docRoot", log.http.docRoot)
    config.set("HTTP", "vhostEnabled", str(log.http.vhostEnabled))
    config.set("HTTP", "vhost", log.http.vhost)
    config.set("HTTP", "auth", str(log.http.auth))
    config.set("HTTP", "realm", log.http.realm)
    config.set("HTTP", "users", json.dumps(log.http.users))
    config.set("HTTP", "userdb", log.http.userdb)

    return config


def getConfigFile():
    if os.path.exists(main.config.localfile):
        return main.config.localfile

    if not os.path.exists(main.config.userdir):
        os.mkdir(os.path.expanduser(main.config.userdir))
    return main.config.userfile


def writeDefaults():
    config = buildDefaults()
    with open(getConfigFile(), "wb") as configFile:
        config.write(configFile)


def updateConfig():
    config = SafeConfigParser()
    config.read(getConfigFile())

    # IRC
    irc.servicename = config.get("IRC", "servicename")
    irc.nick = str(config.get("IRC", "nick"))
    irc.server = str(config.get("IRC", "server"))
    irc.port = int(config.get("IRC", "port"))
    irc.serverPassword = config.get("IRC", "serverPassword") or None
    sslEnabled = config.get("IRC", "sslEnabled")
    if sslEnabled == "True":
        sslEnabled = True
    else:
        sslEnabled = False
    print " *** Config: sslEnabled = %s *** " % sslEnabled
    irc.sslEnabled = sslEnabled
    irc.lineRate = int(config.get("IRC", "lineRate"))

    # Internal SSH Server
    ssh.servicename = config.get("SSH", "servicename")
    ssh.port = int(config.get("SSH", "port"))
    ssh.username = str(config.get("SSH", "username"))
    ssh.keydir = config.get("SSH", "keydir")
    ssh.privkey = config.get("SSH", "privkey")
    ssh.pubkey = config.get("SSH", "pubkey")
    ssh.localdir = config.get("SSH", "localdir")
    ssh.banner = str(config.get("SSH", "banner"))

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
    log.rotate.servicename = config.get("Rotator", "servicename")
    log.rotate.checkInterval = int(config.get("Rotator", "checkInterval"))
    log.rotate.time = config.get("Rotator", "time") 
    log.rotate.maxAgeHours = int(config.get("Rotator", "maxAgeHours"))

    # Log web server
    log.http.servicename = config.get("HTTP", "servicename")
    log.http.port = int(config.get("HTTP", "port"))
    log.http.docRoot = config.get("HTTP", "docRoot")
    log.http.vhostEnabled = bool(config.get("HTTP", "vhostEnabled"))
    log.http.vhost= config.get("HTTP", "vhost")
    log.http.auth = config.get("HTTP", "auth")
    log.http.realm = config.get("HTTP", "realm")

    # Log web server users
    log.http.users = json.loads(config.get("HTTP", "users"))
    log.http.userdb = config.get("HTTP", "userdb")


configFile = getConfigFile()
if not os.path.exists(configFile):
    writeDefaults()
updateConfig()


#del SafeConfigParser, json, os
del Config
#del buildDefaults, configFile, getConfigFile, updateConfig, writeDefaults
del configFile, updateConfig
