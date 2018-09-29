========
Overview
========

项目与版本说明
=====================

ScrapydArt在版本上与Scrapyd保持一致，比如Scrapyd当前版本1.2.0，则ScrapydArt
的版本为1.2.0.n

为了避免增加大家的学习成本，我的编码设计与原scrapyd保持一致，所以在使用上不会给大家
带来困扰，这也是我要写中文文档的原因之一，毕竟都是中国人。如果有国外用户使用，反馈到
我的邮箱，那就再考虑英文文档。

做了哪些改动
=================

因为我每天都使用scrapyd来查看爬虫运行状态，所以我觉得它应该具有更多的爬虫运行信息数
据以及数据统计，以便我们这些爬虫工程师更好的观察和调整。

改动主要涉及几个方面::

    权限控制
    视图
    界面
    API

对，没有错！以前你的爬虫项目通过scrapyd部署到公网服务器，任何人都可以访问它并通过它操
控你的爬虫。现在你可以给ScrapydArt设置用户名和密码，将未通过授权的访问者拒之千里之外。

因为权限管理需要兼容html与json，为此我编写了一个新的视图类。

界面的美观与否因人而异，正所谓::

    我自横刀向天笑，是去是留在我手

对于爬虫运行信息，除了html方面外，我也编写了具有同样功能的API；但是强大的过滤筛选以及排
序功能仅在API开放，后续更多强大的功能也都会着重API方面，它更灵活也更贴近工作需求。

Starting Scrapyd
================

To start the service, use the ``scrapyd`` command provided in the Scrapy
distribution::

    scrapyd

That should get your Scrapyd started.

Scheduling a spider run
=======================

To schedule a spider run::

    $ curl http://localhost:6800/schedule.json -d project=myproject -d spider=spider2
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

For more resources see: :ref:`api` for more available resources.

.. _webui:

Web Interface
=============

Scrapyd comes with a minimal web interface (for monitoring running processes
and accessing logs) which can be accessed at http://localhost:6800/

.. _distutils: http://docs.python.org/library/distutils.html
.. _Twisted Application Framework: http://twistedmatrix.com/documents/current/core/howto/application.html
.. _server command: http://doc.scrapy.org/en/latest/topics/commands.html#server
