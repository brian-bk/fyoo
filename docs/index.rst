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

Fyoo is a simple argument templatizer that wraps around a command.
CLIs exist for pretty much everything, isn't it about time we
started using them in our pipelines as they are? The best data
flow code is code you don't have to write.

Installation
------------

.. code-block:: console

   $ pip install fyoo

Basic Usage
-----------

Fyoo can provide context to a subcommand's arguments after ``--``.
All arguments to that subcommand become pre-rendered jinja2 templates.

Fyoo allows you to inject context into shell arguments in a few
ways, ``--fyoo-set`` being the simplest and easiest to get started
with.

.. code-block:: console
   
   $ fyoo \
     --set table=Employee \
     -- \
   sqlite3 \
     'examples/Chinook_Sqlite.sqlite' \
     'select * from {{ table }} where date(HireDate) < "{{ date() }}"' \
     -csv -header
   ...

This goes further than simple bash replacement, because you have
the full template power of jinja2 between when arguments are
processed and before the process is started.

Let's use this sql template file now.

.. code-block:: sql
   :caption: tests/sql/count.sql.jinja
   :name: count-sql-jinja
   :force:

   {%- if not table %}
     {{ throw("'table' required") }}
   {%- endif %}

   select count(*)
   from {{ table }}
   {%- if condition %}
     where ({{ condition }})
   {%- endif %}

The template file contents are passed as a bash argument, but then
fyoo renders the template before passing it to sqllite3 subcommand.

The ``-v/--verbose`` flag will show the executable before running
it.

.. code-block:: console

   $ fyoo \
     --verbose \
     --jinja-template-folder ./tests/sql \
     --set table=Employee \
     --set condition='lower(Title) like "%sales%"' \
     -- \
   sqlite3 \
     'examples/Chinook_Sqlite.sqlite' \
     '{% include "count.sql.jinja" %}' \
     -csv
   ["sqlite3", "examples/Chinook_Sqlite.sqlite", "\nselect count(*) as c\nfrom Employee\nwhere (lower(Title) like \"%sales%\")", "-csv"]
   4

For complete how-to's and arguments, see :ref:`Usage`.

.. warning::

   Only pass context that you trust! Otherwise you may be leaving yourself
   wide open for `Command Injection`_. Fyoo is suited for use-cases where *you*
   are still directly in control of template context.

Complete Documentation
----------------------

.. toctree::
   :maxdepth: 2

   usage
   cli
   api


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
