import socket

from publishbot import config


class Bot(object):
    """
    """
    def __init__(self):
        self.host = config.listener.host
        self.port = config.listener.port

    def get_bot(self):
        bot = socket.socket()
        bot.connect((self.host, self.port))
        return bot

    def set_topics(self, channels=None, message=None, data=None):
        bot = self.get_bot()
        if not data:
            data = "MULTITOPIC::%s::%s" % (
                ",".join(channels), message)
            bot.sendall(data)
        else:
            for channel, topic in data.items():
                message = "TOPIC::%s::%s" % (
                    channel, topic)
                bot.sendall(data)
        bot.close()

    def broadcast(self, channels, message):
        channels = ",".join(data.keys())
        bot = self.get_bot()
        bot.sendall()
        bot.close()


bot = Bot()
