============
Installation
============

Development
-----------

If you want to develop for bot-prakasha-ke or use the latest code we're working
on, you can install from the sources. You'll need bzr installed, and then just
do the following::

    $ bzr branch lp:bot-prakasha-ke
    $ cd bot-prakasha-ke
    $ sudo python setup.py install

If you prefer git, you can do this:

    $ git clone git@github.com:dreamhost/bot-prakasha-ke.git
    $ cd bot-prakasha-ke
    $ sudo python setup.py install

Pip Install
-----------

You can use pip to get bot-prakasha-ke on your system::

    $ sudo pip install bot-prakasha-ke


Manual Download
---------------

You can manually download the source tarball from the Python Package Index by
visiting the following URL:

    http://pypi.python.org/pypi/bot-prakasha-ke

You'll need to untar and gunzip the source, cd into the source directory, and
then you can do the usual::

    $ sudo python setup.py install


Checking the Source
-------------------

Once installed, you can test the source code by executing this from the
top-level source directory::

    $ trial prakasha

That will run the test suite and report on the success and failure of any unit
tests.
