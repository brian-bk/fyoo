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
   fyoo --fyoo-context='a: A' -- \
     echo '{{ a }}'
   # A

   # but you can always force a particular one
   fyoo --fyoo-context='a: A' --fyoo-context-format=json -- \
     echo '{{ a }}'
   # json.decoder.JSONDecodeError

Context Priority
````````````````


Context dictionaries can be set multiple times, with latest
overriding preceding contexts. However, individually setting
variables will have higher priority, but still behave in the same
ordered-priority.

Priority:

#. Subsequent ``--fyoo-set`` flag
#. Preceding ``--fyoo-set`` flag
#. Subsequent ``--fyoo-context`` flag
#. Preceding ``--fyoo-context`` flag

.. code-block:: bash

   fyoo \
     --fyoo-set=p=higher \
     --fyoo-context='{"p":"lowest"}' \
     --fyoo-set=p=highest \
     --fyoo-context='{"p":"lower"}' \
     -- \
     echo '{{ p }}'
     # highest

Built-in Templating
-------------------


.. autoclass:: fyoo.internal.template.FyooDatetimeExtension
   :members:
   :exclude-members: parse
.. autoclass:: fyoo.internal.template.FyooEnvExtension
   :members:
   :exclude-members: parse
.. autoclass:: fyoo.internal.template.FyooThrowExtension
   :members:
   :exclude-members: parse


Complete CLI Reference
----------------------

.. argparse::
   :ref: fyoo.cli.get_parser
   :prog: fyoo
