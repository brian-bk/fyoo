.. _usage:

Usage
=====

Examples
--------

Context Formatter
`````````````````

Set common context variables with auto, json, or yaml format.

.. code-block:: bash

   # auto will attempt different context formats
   fyoo --fyoo-context='a: A' \
     -- \
   echo '{{ a }}'
   # A

   # but you can always force a particular one
   fyoo --fyoo-context='a: A' --fyoo-context-format=yaml \
     -- \
   echo '{{ a }}'
   # A

   fyoo --fyoo-context='a: A' --fyoo-context-format=json \
     -- \
   echo '{{ a }}'
   # json.decoder.JSONDecodeError

Context Priority
````````````````

Context dictionaries can be passed multiple times, with latest
overriding preceding contexts. In addition, ``--fyoo-set`` will
have higher priority than ``--fyoo-context``.

Priority:

#. Latest ``--fyoo-set`` flag (Highest priority)
#. Earliest ``--fyoo-set`` flag
#. Latest ``--fyoo-context`` flag
#. Earliest ``--fyoo-context`` flag (Lowest priority)

.. code-block:: bash

   fyoo \
     --fyoo-set=p=higher \
     --fyoo-context='{"p":"lowest"}' \
     --fyoo-set=p=highest \
     --fyoo-context='{"p":"lower"}' \
     -- \
   echo '{{ p }}'
   # highest

Complete CLI Reference
----------------------

.. argparse::
   :ref: fyoo.cli.get_parser
   :prog: fyoo

Built-in Templating
-------------------

Datetime Helpers
````````````````

Also see :py:class:`fyoo.template.FyooDatetimeExtension`.

date()
++++++

Print a timestamp in specified timezone and format.

.. code-block:: bash

   fyoo -- echo '{{ date() }}'
   # 2020-01-01
   fyoo -- echo 'we all miss {{ date(tz="EST", fmt="%Y%m%d") }}'
   # we all miss 20191231

dt()
++++

Alias for `date()`_.

raw_datetime
++++++++++++

The actual ``datetime.datetime`` object. Work with it however
you would like.

Also see :py:class:`fyoo.template.FyooEnvExtension`.

Environment Helpers
```````````````````

Helpers to environment variables (and maybe later
more 'environmenty' things).

getenv()
++++++++

Pass through to ``os.getenv(*args, **kwargs)``.

.. code-block::

   fyoo -- echo '{{ getenv("USER") }}'
   # acooluser

.. code-block::

   fyoo -- echo '{{ getenv("SOMEVAR", "thatwasntthere") }}'
   # thatwasntthere

Throw Helpers
`````````````

Extension to throw/raise an exception from a template.

Also see :py:class:`fyoo.template.FyooThrowExtension`.

throw()
+++++++

"Throw" (raise) an exception. Terminology is mixed
to not use python term.

.. code-block:: sql
   :caption: count.tpl.sql
   :name: count-tpl-sql

   {%- if not table %}
     {{ throw("no 'table' provided :(") }}
   {%- endif %}

   select count(*)
   from {{ table }}

.. code-block:: bash

   fyoo -- echo "$(cat count.tpl.sql)"
   # fyoo.exception.FyooTemplateException: no 'table' provided :(
