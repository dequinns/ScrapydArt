==========
ScrapydArt
==========

.. image:: https://secure.travis-ci.org/scrapy/scrapyd.svg?branch=master
    :target: http://travis-ci.org/scrapy/scrapyd

.. image:: https://codecov.io/gh/scrapy/scrapyd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/scrapy/scrapyd



ScrapydArt 权限功能停用通知
----------

原因：Scrapyd 与 Scrapyd-client 是紧密关联的关系，虽然我改动了 Scrapyd ，但是没有改动关联的 Scrapyd-client 。导致现在使用命令 scrapyd-deploy 打包部署到 ScrapydArt 时会出现无权限的提示。 
解决：目前有几个解决办法

1、我将 Scrapyd-client 也一并改了；

2、大家暂时不要启用 ScrapydArt 的权限功能；

3、我正在和大佬们开发新的爬虫管理调度平台，平台定位很高，要做很强的平台，大家可以稍微等一段时间，用新平台（推荐）。

拒绝裸奔
----------

ScrapydArt在Scrapyd基础上新增了权限验证、筛选过滤、排序、数据统计以及排行榜等功能，并且有了更强大的API。


    scrapyd是世界最优秀的爬虫框架scrapy官方提供的部署控管理平台，它提供了爬虫任务调用的api、爬虫运行日志功能。

但它并不提供权限验证功能，意味着只要你部署到服务器，任何人都可以访问它并且控制你的爬虫。它也不提供数据统计的功能，你不可能知道你部署的爬虫有多少、也不知道它们运行了多少次、谁的运行时间最长、更别说排行了。官方开发人员关注的重点是api功能性而非界面，所以界面（甚至可以说没有界面）不谈美观。


ScrapydArt安装：

```
pip install scrapydart
```
        

ScrapydArt启动命令：

 ```scrapydart```


ScrapydArt-web界面：

```http://localhost:6800```


更多使用方法和ScrapydArt的详细介绍请阅读ScrapydArt文档
--------------------------------------------------

    https://scrapydart.readthedocs.io/zh/latest/


下图为ScrapydArt界面
--------------------

.. image:: https://github.com/dequinns/ScrapydArt/blob/master/images/scrapydart-home.png

.. image:: https://github.com/dequinns/ScrapydArt/blob/master/images/scrapydart-jobs.png

ScrapydArt base on Scrapyd, and added auth/filter/order…… and added new API

ScrapydArt is a service for running `Scrapy`_ spiders.

It allows you to deploy your Scrapy projects and control their spiders using an
HTTP JSON API.

The documentation (including installation and usage) can be found at(官方文档在此):
https://scrapydart.readthedocs.io/zh/latest/

.. image:: https://github.com/dequinns/ScrapydArt/blob/master/images/scrapydart-doc.png

.. _Scrapy: https://github.com/dequinns/scrapydart
