========
概述
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
    配置文件


#. 对，没有错！以前你的爬虫项目通过scrapyd部署到公网服务器，任何人都可以访问它并通过它操控你的爬虫。现在你可以给ScrapydArt设置用户名和密码，将未通过授权的访问者拒之千里之外。
#. 因为权限管理需要兼容html与json，为此我编写了一个新的视图类。
#. 界面的美观与否因人而异，正所谓 ``我自横刀向天笑，是去是留在我手``
#. 对于爬虫运行信息，除了html方面外，我也编写了具有同样功能的API；但是强大的过滤筛选以及排序功能仅在API开放，后续更多强大的功能也都会着重API方面，它更灵活也更贴近工作需求。
#. 由于将scrapyd的目录重新命名成scrapydart，所以在配置文件中对应的名称也需要改动过来，否则启动失败。


Starting ScrapydArt
================

如果你想要启动scrapydart服务, 可以使用命令 ``scrapydart`` 来启动，而不是之前使用的 ``scrapyd`` ::

    scrapydart

然后你就会看到你的scrapydart服务成功启动。

爬虫的调度
=======================

爬虫运行调度跟scrapyd是一模一样的，这方面保持一致::

    $ curl http://localhost:6800/schedule.json -d project=myproject -d spider=spider2
    {"status": "ok", "jobid": "26d1b1a6d6f111e0be5c001e648c57f8"}

更多好用的API请参阅: :ref:`api`  文档  ``只有文档才能让你变得更强``

.. _webui:

Web 操作界面
=============

ScrapydArt的界面功能要比Scrapyd要丰富一些，除了原有的观察运行情况信息之外，还新增了统计、汇总
以及排序信息，让你能够更好的了解项目和爬虫运行状态，比如::

    到底哪些爬虫被调用过，哪些又从未被调用过？

    被调用次数最多的爬虫是哪一个？

    现有爬虫的平均运行时长是多久？

    我还想知道运行时间最长的那个爬虫到底运行了多久？

    我的Alibaba项目里面，到底有哪几个spider，spider name 对应的是什么？

启动ScrapydArt服务后打开浏览器，访问http://localhost:6800/ 就可以得到你想要的答案。

.. _distutils: http://docs.python.org/library/distutils.html
.. _Twisted Application Framework: http://twistedmatrix.com/documents/current/core/howto/application.html
.. _server command: http://doc.scrapy.org/en/latest/topics/commands.html#server
