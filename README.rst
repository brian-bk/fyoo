Fyoo
====

*A CLI for the containerized data orchestration world*

|PyPI Package|
|Documentation| 
|Git tag|
|Test status|
|Code coverage|

.. |PyPI Package| image:: https://img.shields.io/pypi/v/fyoo.svg
   :target: https://pypi.python.org/pypi/fyoo/
.. |Documentation| image:: https://readthedocs.org/projects/fyoo/badge/?version=develop
    :target: https://fyoo.readthedocs.io/en/develop/?badge=develop
    :alt: Documentation Status
.. |Git tag| image:: https://img.shields.io/github/tag/brian-bk/fyoo.svg
   :target: https://github.com/brian-bk/fyoo/commit/
.. |Test status| image:: https://circleci.com/gh/brian-bk/fyoo/tree/develop.svg?style=svg
    :target: https://circleci.com/gh/brian-bk/fyoo/tree/develop
.. |Code coverage| image:: https://codecov.io/gh/brian-bk/fyoo/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/brian-bk/fyoo

Fyoo is a consistent, extendable, templated CLI for dataflow operations.
Fyoo makes sure that the individual tasks in data orchestration behave
in the same way, so that every building block is easily understood
and glued together.

Quickstart
``````````

You can install Fyoo from PyPI:

.. code-block:: bash

    pip install fyoo

.. note::

    `Pipenv <https://pipenv-fork.readthedocs.io>`_ is the best deterministic dependency tool for adding Fyoo to containers at build time.

Fyoo provides two main features for those using the Fyoo CLI:

* Consistent templating
* Consistent resource configuration

Templated Arguments
+++++++++++++++++++

The simplest flow (subparser) built in is ``hello``, which
has an optional argument for the message. All arguments
on the flow are templated, if they are strings.

.. code-block:: bash

   fyoo hello --message 'The date is {{ date() }}'
   # The date is 2020-02-25

But arguments on Fyoo precurse the Flow subcommand, so
you can provide context in the same way on every different
Flow.

.. code-block:: bash

    # Arguments to fyoo will always be the same, 
    # to the flow may be different
    fyoo --jinja-context='{"a": "any_var"}' \
      hello --message 'Hello {{ a }}'

    fyoo --jinja-context='{"a": "any_var"}' \
      touch '{{ a }}.txt'
    ls -Ut | head -1
    # any_var.txt

Resource Configuration
++++++++++++++++++++++

Fyoo resources are configured in a single way for all Flows.
Simply add to a ``fyoo.ini`` file, and run Fyoo from the same
directory.

.. code-block:: ini

    # fyoo.ini

    [postgres]
    username = postgres
    password = %(POSTGRES_PASSWORD)s
    host = 127.0.0.1

.. code-block:: bash

    # Run postgres in the background
    docker run --name fyoo-pg \
        -e POSTGRES_PASSWORD=secretpass \
        -p 5432:5432 \
        -d postgres

    POSTGRES_PASSWORD=supersecret \
    fyoo \
      postgres_query_to_csv_file \
      'select {{ date() }} as d' out.csv

Templating and Resources
++++++++++++++++++++++++

The real power of Fyoo comes together when you use templating
and resources together. Template and resource specification
(not including precise resource credentials) are known beforehand.
So at runtime the executable can remain consistent.

Here is an example putting it all together.
We use the contents of a sql template file to run a
query, and output to a csv file of the current date.

.. code-block:: sql

    -- pg.tpl.sql

    {% for i in range(0, num) %}
      {% if not loop.first %}union all{% endif %}
      select {{ i }} as a
    {% endfor %}


.. code-block:: bash

    POSTGRES_PASSWORD=supersecret \
    fyoo \
        --jinja-context '{"num": 5}' \
        postgres_query_to_csv_file \
        "$(cat pg.tpl.sql)" \
        'results-{{ date() }}.csv'

Building Flows
``````````````

Fyoo decorators allow you to create functions quickly using
standard argparse arguments and Fyoo's resources.

A minimalist example of the postgres_query_to_csv_file flow
is shown below. ``@fyoo.argument`` adds arguments to the CLI arguments,
and ``@fyoo.resources`` adds FyooResource types which are configured
at runtime by ``fyoo.ini``.

.. code-block:: python

    @fyoo.argument('--query-batch-size', type=int, default=10_000)
    @fyoo.argument('target')
    @fyoo.argument('sql')
    @fyoo.resource(MysqlResource)
    @fyoo.flow()
    def mysql_query_to_csv_file(
            mysql: Connection,
            sql: str,
            target: str,
            query_batch_size: int,
    ):
        result_proxy: ResultProxy = mysql.execute(sql)

        with open(target, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(result_proxy.keys())
            while result_proxy.returns_rows:
                rows = result_proxy.fetchmany(query_batch_size)
                if not rows:
                    break
                writer.writerows(rows)
