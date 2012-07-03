====
TODO
====

Known Issues
------------

* when a user nick changes, the change is logged on all channels, even if that
  user is not logged into one of the channels

* when ``make generate-config`` is called, if the file already exists, it is
  not backed up -- simply removed


New Features
------------

* add in-line image (logo) to README

* add notes in README about launchpad project URL, blueprint usage, code repos,
  where to submit bugs, patches, etc.

* fix usage notes

* fix initial screen re-draw after login with terminal.app on Mac OS X

* add support for scheduling messages

* add support for setting/updating the bot's schedule

* add support for passing JSON as a command, e.g.:
  $ ssh -p 6622 localhost "<json * data>"

* add tab-completion to the shell

* when the logger first signs on, log the users who are currently on channel

* add support for an additional authorized_keys file, so that access to the
  bot's shell may be possible without granting access to the machine/account it
  is hosted on

* add an RSS/Atom listener that posts updates to IRC when new commits come in,
  e.g.: https://github.com/dreamhost/bot-prakasha-ke/commits/master.atom

* generate and host RSS/Atom feeds from pre-defined sources

* accept POSTs of data (RSS or Atom feeds/plain text/JSON) for publishing
  and/or consumption by an appropriate processor.

* add sftp support to the bot (scp was a no-go)

  * if a file is uploaded, where does it go? maybe create a "files" dict in the
    namespace, and save in the dict?

  * where does the last git file live?

  * how do we compare them?

  * how do we replace one for the other?

  * once compared, how do we extract the "new commits" and post those to the
    IRC bot?

  * override openFile to use MemorySFTPFile?

  * override openDirectory to use MemorySFTPDirectory?

  * for the code that's been added so far, take it out of shell, and put it
    into upload.
