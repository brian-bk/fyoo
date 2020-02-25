.. Fyoo documentation master file, created by
   sphinx-quickstart on Sun Feb 23 22:57:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fyoo's documentation!
================================

Fyoo is a consistent, extendable, templated CLI for dataflow operations.
Fyoo makes sure that the individual tasks in data orchestration behave
in the same way, so that every building block is easily understood
and glued together.

CLI Examples
````````````

Templated Arguments
+++++++++++++++++++

The simplest flow (subparser) built in is `hello`, which
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

Resources
+++++++++

TODO!

Design
``````

Fyoo Flows are designed to be stateless, as far as Fyoo context is concerned.
This lets you orchestrate however you see fit. If adding Fyoo is part of your
container build time, executing Fyoo Flows is especially easy.

Some popular container-based orchestrators include:

* Argo
* K8s CronJobs (if you just need scheduling and not orchestration)
* Airflow (with DockerOperators or KubernetesPodOperators)

But anything that can run a container can very easily run Fyoo Flows.

.. include:: contents.rst.inc


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
