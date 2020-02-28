.. _usage:

Running Fyoo Flows
==================

Basic Commands
--------------

Fyoo manages between executing a subparser on
the command-line and injecting in functional arguments.
Fyoo is consistent about how it behaves when calling
a function - but any function itself is completely
unique.

All Fyoo Flow subparser arguments are are contextually
processed templates.

Built-in Templating
```````````````````

.. autoclass:: fyoo.template.DatetimeExtension
    :members: date, now

Runtime Templating
``````````````````

Context can also be provided at runtime by specifying
a json blob to the ``--jinja-context`` argument on ``fyoo``.

.. code-block:: bash

    fyoo --jinja-context='{"a": "any_var"}' \
      hello --message 'Hello {{ a }}!'
    # Hello any_var!

Configuring Resources
---------------------

Fyoo resources are configured with a config file
``fyoo.ini``. This is where you should keep all your
resource specification of what is required. But
environment variables can be added in with i.e. ``%(USER)s``.
Not all environment variables are always safe to pass through
to the ``fyoo.ini`` configuration file. This is the list
of environment variables you have access to:

* ``PATH``
* ``PYTHONPATH``
* ``PWD``
* ``HOME``
* ``USER``
* ``FYOO_`` (with any following suffix)

At CLI runtime, by default the name of the Fyoo resource
will be the configuration is used. However, Fyoo recognizes
that sometimes a different resource is needed. Fyoo adds
the ``--{resource_name}`` argument to a Flow that uses it,
so you can specify which resource to use at runtime.

For example, if you have a configuration file:

.. code-block:: ini

    # fyoo.ini

    [postgres]
    username = postgres
    password = %(FYOO_POSTGRES_PASSWORD)s
    host = 127.0.0.1

    [a_cooler_postgres]
    username = postgres
    password = %(FYOO_POSTGRES_PASSWORD)s
    host = else.where.location

You may call either command:

.. code-block:: bash

    # This will use the default resource name, which
    # is 'postgres'
    FYOO_POSTGRES_PASSWORD=supersecret \
    fyoo \
      postgres query_to_csv_file \
      'select 1'

    # This will use the other postgres
    FYOO_POSTGRES_PASSWORD=supersecret \
    fyoo \
      postgres query_to_csv_file \
      --postgres=a_cooler_postgres \
      'select 1'

If a Flow itself needs access to multiple resources
of the same type, it should specify which resource
to use as a required argument. Let's imagine that
there is a Flow that queries from one postgres
database and writes to a different one. If "source"
and "target" are how the Flow wants to distinguish
the two different resources, it would have two
arguments ``--postgres-source`` and ``--postgres-target``.

.. code-block:: bash

     FYOO_POSTGRES_PASSWORD=supersecret \
    fyoo \
      postgres query_to_csv_file \
      # let --postgres-source be postgres
      --postgres-target=a_cooler_postgres \
      'select 1'
 