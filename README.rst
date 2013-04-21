.. image:: resources/images/logox128.png
   :align: right

about
-----

bot-prakasha-ke is an IRC bot which does the following:

* connects to arbitrary channels on an IRC host
* logs those channels (topics and conversations)
* broadcasts messages or changes topics
* offers a web service view viewing recorded logs
* offers an ssh shell of the running bot for batch-updating channel topics
  or broadcasting messages
* allows one to use the ssh command to script broadcast messages, topic
  updates, etc., e.g.::
    ssh -p 6622 127.0.0.1 "say('#cool-channel', 'Have a good night!')"

quick start
-----------

If you install with pip, the dependencies will be added for you::

  $ pip install .

To run the server with the defaults, simply do this::

  make run

That will log to stdout, so it's nice for debugging. If you want to run as a
daemon::

  make daemon

To stop the daemon::

  make stop


configuration
-------------

A configuration file is automatically generated when you do ``make run`` or
``make daemon``. However, if you'd like to pre-generate the config file so that
you can edit it prior to running the server, you can do this::

  make generate-config

WARNING!

    Running the make target ``make generate-config`` will overwrite your
    existing configuration! Backup your configuration file before using!


contributions
-------------

Project planning is done here: https://blueprints.launchpad.net/bot-prakasha-ke

File bugs here: https://github.com/oubiwann/bot-prakasha-ke/issues/new

Authors hang out on Frenode here: #adytum
