Usage
=====

Installation
-------------

.. note::
    Fyoo requires python3

You can install the latest version of Fyoo with:

::

    pip install fyoo

Using the CLI
-------------

.. argparse::
    :ref: fyoo.cli.get_parser
    :prog: fyoo

Resource Configuration
----------------------

.. code-block:: ini
    :caption: fyoo.ini
    :name: fyoo-ini

    [mysql]
    username = root
    password = %(FYOO_MYSQL_PASS)s
    host = 127.0.0.1
