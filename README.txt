Publish-Bot
-----------

Publish-Bot is an IRC bot which simply listens on a TCP port and
relays messages to IRC. It's meant for applications which want to
notify IRC channels of events without implementing their own IRC code.

To start a publish-bot service, first edit config.py and then run
`twistd -y bot.tac'.

Connect to LISTENER_PORT and send lines of the form:

  LISTENER_PASSWORD:#channel:message

the bot will join #channel (if it's not already there) and send the message.

TODO: multiple IRC server support.

Bazaar commit hook
------------------

There's a bzr commit hook in bzrcommitmessage.py, which will send your
commit messages to a Publish-bot service so that you can see your
commits in an IRC channel.

To use it, symlink it into ~/.bazaar/plugins, then edit
~/.bazaar/locations.conf, creating or editing an entry for whatever
branch or branch hierarchy you want the hook to apply to, like so:

[/home/radix/Projects/myproj]
post_commit = bzrlib.plugins.bzrcommitmessage.send_commit
message_host = commitbot.example.com
message_port = 1234
message_password = yay
message_channel = bottest
message_branch_prefix = myproj

The message_branch_prefix configuration parameter is optional.  When
present it will be prepended to the name of the branch in the form:
branch_prefix/branch_name.  This is useful when you need to
disambiguate branches with the same names for different projects, such
as for client/server applications.  Also, notice that the channel does
NOT include a leading hash mark ('#').

Now any commits that happen under /home/radix/Projects/myproj
will send a message to #bottest.
