Edit config.py
run twistd -y bot.tac

Then connect to LISTENER_PORT and send lines like

LISTENER_PASSWORD:#channel:message

the bot will join #channel (if it's not already there) and send the message.

Bazaar commit hook
------------------

There's a bzr commit hook in bzrcommitmessage.py. Edit it to specify
configuration details about your listener and the channel to send to.

Copy it to ~/.bazaar/plugins, then edit ~/.bazaar/locations.conf, creating or
editing an entry for whatever branch or branch hierarchy you want the hook to
apply to, like so:

[/home/radix/Projects/myproj]
post_commit = bzrlib.plugins.bzrcommitmessage.post_commit

