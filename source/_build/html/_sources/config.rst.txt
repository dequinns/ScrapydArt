.. _config:

配置文件
==================

配置文件的路径与Scrapyd保持一致，在python环境的包安装目录（site-packages）下,比如

/anaconda3/lib/python3.6/site-packages/

目录名称为scrapydart

新增的API配置已然加入其中

对于访问权限控制的配置，你可以在文档的[权限控制]中找到配置方法与使用方法



The configuration file supports the following options (see default values in
the :ref:`example <config-example>`).

http_port
---------

The TCP port where the HTTP JSON API will listen. Defaults to ``6800``.

bind_address
------------

The IP address where the website and json webservices will listen.
Defaults to ``127.0.0.1`` (localhost)

.. _max_proc:

max_proc
--------

The maximum number of concurrent Scrapy process that will be started. If unset
or ``0`` it will use the number of cpus available in the system multiplied by
the value in ``max_proc_per_cpu`` option. Defaults to ``0``.

.. _max_proc_per_cpu:

max_proc_per_cpu
----------------

The maximum number of concurrent Scrapy process that will be started per cpu.
Defaults to ``4``.

debug
-----

Whether debug mode is enabled. Defaults to ``off``. When debug mode is enabled
the full Python traceback will be returned (as plain text responses) when there
is an error processing a JSON API call.

eggs_dir
--------

The directory where the project eggs will be stored.

dbs_dir
-------

The directory where the project databases will be stored (this includes the
spider queues).

logs_dir
--------

The directory where the Scrapy logs will be stored. If you want to disable
storing logs set this option empty, like this::

    logs_dir =

.. _items_dir:

items_dir
---------

.. versionadded:: 0.15

The directory where the Scrapy items will be stored.
This option is disabled by default
because you are expected to use a database or a feed exporter.
Setting it to non-empty results in storing scraped item feeds
to the specified directory by overriding the scrapy setting ``FEED_URI``.

.. _jobs_to_keep:

jobs_to_keep
------------

.. versionadded:: 0.15

The number of finished jobs to keep per spider.
Defaults to ``5``.
This refers to logs and items.

This setting was named ``logs_to_keep`` in previous versions.

.. _finished_to_keep:

finished_to_keep
----------------

.. versionadded:: 0.14

The number of finished processes to keep in the launcher.
Defaults to ``100``.
This only reflects on the website /jobs endpoint and relevant json webservices.

poll_interval
-------------

The interval used to poll queues, in seconds.
Defaults to ``5.0``.
Can be a float, such as ``0.2``

runner
------

The module that will be used for launching sub-processes. You can customize the
Scrapy processes launched from Scrapyd by using your own module.

application
-----------

A function that returns the (Twisted) Application object to use. This can be
used if you want to extend Scrapyd by adding and removing your own components
and services.

For more info see `Twisted Application Framework`_

.. _webroot:

webroot
-------

A twisted web resource that represents the interface to scrapyd.
Scrapyd includes an interface with a website to provide simple monitoring
and access to the application's webresources.
This setting must provide the root class of the twisted web resource.

node_name
---------

.. versionadded:: 1.1

The node name for each node to something like the display hostname. Defaults to ``${socket.gethostname()}``.

.. _config-example:

Example configuration file
--------------------------

Here is an example configuration file with all the defaults:

.. literalinclude:: ../scrapydart/default_scrapyd.conf
.. _Twisted Application Framework: http://twistedmatrix.com/documents/current/core/howto/application.html
