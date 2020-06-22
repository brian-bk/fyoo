.. Fyoo documentation master file, created by
   sphinx-quickstart on Sun Feb 23 22:57:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst
   :start-after: links

Fyoo
====

|PyPI Package|
|Documentation| 
|Git tag|
|Test status|
|Code coverage|

Fyoo is a simple jinja2-based command-argument-templatizer CLI utility.
Templatizing can be done at runtime for consistent argument tweaks.

Basic Usage
-----------

Fyoo runs a command with templatized arguments succeeding `--`. Context
can be provided by flags or there are a few baked-in functions.

Example inline query:

.. code-block:: bash

   # Create a sqlite3 db for this example
   sqlite3 example.db 'create table if not exists user (username string, created date default current_date);insert into user(username) values ("cooluser")'
   
   # run a templatized/dynamic query to csv output
   fyoo --fyoo-set table=user --fyoo-set db=example.db -- \
     sqlite3 '{{ db }}' \
      'select * from {{ table }} where date(created) = "{{ dt() }}"' \
      -csv -header
   # username,created
   # cooluser,2020-06-21

If SQL queries are to be re-used, perhaps the query itself comes from a template file.

.. code-block:: bash

   echo 'select count(*)
   from {{ table }}' > count.sql
   
   fyoo '--fyoo-context={"db": "example.db", "table": "user"}' -- \
     sqlite3 '{{ db }}' "$(cat count.sql)"
   # 1 (assuming same example from before)


For complete how-to's and arguments, see :ref:`Usage`.

Complete Documentation
----------------------

.. toctree::
   :maxdepth: 2

   usage
   api


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
