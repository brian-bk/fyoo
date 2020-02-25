.. Fyoo documentation master file, created by
   sphinx-quickstart on Sun Feb 23 22:57:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fyoo's documentation!
================================

Fyoo is a consistent, extendable, templated CLI for dataflow operations.
Fyoo makes sure that the individual tasks in data orchestration behave
transparently, so that every building block is understood.

In addition, Fyoo Flows are easy to write with templatizing and resources built in.
You can focus on how you will move data, and less about the same boilerplate pipeline
code.

Quick Examples
``````````````

Pass in context from arguments::

   fyoo \
      --jinja-context='{"a": "A value!"}' \
      hello \
      --message='well there is {{ a }}'

Output metadata as json::

   touch file.txt
   fyoo \
      --flow-report-file=out.json \
      move \
      file.txt \
      'file_{{ datetime.now().strftime("%Y%m%d") }}.txt'
   cat out.json | python -m json.tool
   {
       "metadata": {
           "start": "2020-02-24T00:05:46.183910",
           "end": "2020-02-24T00:05:46.184036",
           "duration": 0.00012564659118652344,
           "flow": {
               "name": "move",
               "file": "/home/somebody/fyoo/fyoo/ext/common/flow.py"
           }
       },
       "kwargs": {
           "source": "file.txt",
           "target": "file_20200224.txt"
       },
       "result": null
   }

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
