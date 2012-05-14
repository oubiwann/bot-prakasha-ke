from twisted.application.service import ServiceMaker


BotPrakashaService = ServiceMaker(
    "Bot Prakasha Ke",
    "prakasha.app.service",
    ("A Twisted-based IRC bot, complete with HTTP log browser and interactive "
     "SSH shell."),
    "prakasha")  
