Fyoo
====

*A CLI for the containerized data orchestration world*

|PyPI Package|
|Documentation| 
|Git tag|
|Test status|
|Code coverage|


Fyoo is a consistent, extendable, templated CLI for dataflow operations.
Fyoo makes sure that the individual tasks in data orchestration behave
in the same way, so that every building block is easily understood
and glued together.

Using Flows
```````````

You can install Fyoo from PyPI:

.. code-block:: bash

    pip install fyoo

Note: Pipenv_ is the best deterministic dependency tool for building applications.

Fyoo provides two main features for those using the Fyoo CLI:

* Consistent templating
* Easy resource configuration

Templated Arguments
+++++++++++++++++++

The simplest flow (subparser) built in is ``hello``, which
has an optional argument for the message. All arguments
on every flow are templated, assuming the argument type is a string.

.. code-block:: bash

   fyoo hello --message 'The date is {{ date() }}'
   # The date is 2020-02-25

But arguments on Fyoo precurse the Flow subcommand, so
you can provide context in the same way on every different
Flow. Arguments to `fyoo` will always be the same, 
but the Flow subcommand may have any arguments it wishes.

.. code-block:: bash

    # `hello` has an optional argument --message,
    # and `touch` has a required argument filename.
    # But both receive context from the --jinja-context
    # argument on `fyoo`.

    fyoo --jinja-context='{"a": "any_var"}' \
      hello --message 'Hello {{ a }}!'
    # Hello any_var!

    fyoo --jinja-context='{"a": "any_var"}' \
      touch '{{ a }}.txt'
    ls -Ut | head -1
    # any_var.txt

Resource Configuration
++++++++++++++++++++++

Note: Run postgres in the background if you'd like to
try the following examples:

.. code-block:: bash

    docker run --name fyoo-pg \
        -e POSTGRES_PASSWORD=secretpass \
        -p 5432:5432 \
        -d postgres

Fyoo resources are configured in a single way for all Flows.
Simply add to a ``fyoo.ini`` file, and run Fyoo from the same
directory.

.. code-block:: ini

    # fyoo.ini

    [postgres]
    username = postgres
    password = %(FYOO_POSTGRES_PASSWORD)s
    host = 127.0.0.1

.. code-block:: bash

    FYOO_POSTGRES_PASSWORD=supersecret \
    fyoo \
      postgres_query_to_csv_file \
      'select {{ date() }} as d' out.csv
    cat out.csv
    # d
    # "2020-01-01"

Running it All Together
+++++++++++++++++++++++

The real power of Fyoo comes together when you use templating
and resources together. Template and resource specification
are generally static, so they can and should be declaratively
set (with particular resource credentials provided at runtime).
This means that executable arguments never change.

Here is an example putting it all together.
We use the contents of a sql template file to run a
query, and output to a csv file of the current date.

.. code-block:: sql

    -- table_counter.tpl.sql

    {% for i in range(0, num) %}
      {% if not loop.first %}union all{% endif %}
      select {{ i }} as a
    {% endfor %}


.. code-block:: bash

    FYOO_POSTGRES_PASSWORD=supersecret \
    fyoo \
      --jinja-context '{"num": 5}' \
      postgres_query_to_csv_file \
      "$(cat table_counter.tpl.sql)" \
      'results-{{ date() }}.csv'

Building Flows
``````````````

Flows are Fyoo's subcommands, which are written as functions.
Fyoo decorators allow you to build custom CLIs quickly and
easily. When writing a Flow, you simply need to know your arguments
and ``FyooResource``'s that you will use. There are three main decorators.

``@fyoo.flow`` will do one thing:

#. *Usage*: Expose your Flow function as a CLI subcommand of `fyoo`

Once you have a Flow, ``@fyoo.argument`` will do two things
if your Flow needs arguments:

#. *Usage*: Add an argparse argument to the Flow CLI
#. *Implementation*: Add a templated in version of that CLI argument
   as a keyword argument to the Flow function,

Lastly, ``@fyoo.resource`` will do one thing if your
Flow needs a resource:

#. *Usage*: Add that resource as a keyword argument to the Flow function,
   based on the contents of ``fyoo.ini``.

Here is a minimalist example of ``fyoo postgres_query_to_csv_file``,
with less optional arguments than the real version:

.. code-block:: python

    @fyoo.argument('--query-batch-size', type=int, default=10_000)
    @fyoo.argument('target')
    @fyoo.argument('sql')
    @fyoo.resource(PostgresResource)
    @fyoo.flow()
    def postgres_query_to_csv_file(
            postgres: Connection,
            sql: str,
            target: str,
            query_batch_size: int,
    ):
        result_proxy: ResultProxy = postgres.execute(sql)

        with open(target, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(result_proxy.keys())
            while result_proxy.returns_rows:
                rows = result_proxy.fetchmany(query_batch_size)
                if not rows:
                    break
                writer.writerows(rows)

.. links

.. |PyPI Package| image:: https://img.shields.io/pypi/v/fyoo.svg
   :target: https://pypi.python.org/pypi/fyoo/
.. |Documentation| image:: https://readthedocs.org/projects/fyoo/badge/?version=latest
    :target: https://fyoo.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |Git tag| image:: https://img.shields.io/github/tag/brian-bk/fyoo.svg
   :target: https://github.com/brian-bk/fyoo/commit/
.. |Test status| image:: https://circleci.com/gh/brian-bk/fyoo/tree/master.svg?style=svg
    :target: https://circleci.com/gh/brian-bk/fyoo/tree/master
.. |Code coverage| image:: https://codecov.io/gh/brian-bk/fyoo/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/brian-bk/fyoo
.. _Pipenv: https://pipenv-fork.readthedocs.io/
