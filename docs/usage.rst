.. _usage:

Usage
=====

Context
-------

Passing Dictionaries
````````````````````

Set common context variables with json or yaml format.
The default context format is json.

.. code-block:: bash

   fyoo --context='{"a":"A"}' \
     -- \
   echo '{{ a }}'
   # A

   fyoo --context='a: A' --context-format=yaml \
     -- \
   echo '{{ a }}'
   # A


Context Priority
````````````````

Context dictionaries can be passed multiple times, with latest
overriding preceding contexts. In addition, ``--set`` will
have higher priority than ``--context``.

Priority:

#. Latest ``--set`` flag (Highest priority)
#. Earliest ``--set`` flag
#. Latest ``--context`` flag
#. Earliest ``--context`` flag (Lowest priority)

.. code-block:: console

   $ fyoo \
     --set=p=higher \
     --context='{"p":"lowest"}' \
     --set=p=highest \
     --context='{"p":"lower"}' \
     -- \
   echo '{{ p }}'
   highest

Templating
----------

Jinja Controls
``````````````

There are several jinja controls that allow heavy customization to
how Fyoo's jinja templating works, if desired. Many of these have
corresponding environment variables, in the expectation of setting
them in a Dockerfile.

For example, ``FYOO__JINJA_TEMPLATE_FOLDER`` can be really powerful
in setting the location of ``-jtf/--jinja-template-folder`` at
container build time.

.. literalinclude:: Dockerfile
   :language: dockerfile
   :caption: docs/Dockerfile
   :name: dockerfile

.. code-block:: console

   $ docker build . -f docs/Dockerfile -t fyoo-example
   $ docker run fyoo-example \
       fyoo --dry-run --set table=customer \
         -- \
       sqlite3 '{% include "count.sql.jinja" %}'
   ["sqlite3", "\nselect count(*) as c\nfrom customer"]

Other jinja controls such as extensions and block string settings
are in :doc:`cli`.


Built-in Reference
``````````````````

.. automodule:: fyoo.template.attributes
   :members:

.. automodule:: fyoo.template.filters
   :members:
