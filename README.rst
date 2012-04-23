about
-----

bot-prakasha-ke is an IRC bot which does the following:
 * connects to arbitrary channels on an IRC host
 * logs those channels (topics and conversations)
 * broadcasts messages or changes topics
 * offers a web service view viewing recorded logs
 * offers an ssh service into the running bot for batch-updating channel topics
   or broadcasting messages

quick start
-----------

If you install with pip, the dependencies will be added for you::

  $ pip install .

To run the server with the defaults, simply do this::

  make run

That will log to stdout, so it's nice for debugging. If you want to run as a
daemon::

  make daemonize

To stop the daemon::

  make kill


configuration
-------------

TBD
