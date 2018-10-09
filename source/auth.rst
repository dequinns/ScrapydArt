.. _auth:
============
权限控制
============


访问权限控制
------------

Scrapyd未提供访问权限控制功能，意味着只要你将爬虫项目部署到公网上，别人就可以任意访问和操控你的爬虫，这听起来很刺激。
当然，你也可以借助别的工具实现访问权限控制，比如Nginx，但是当你在调用API的时候，就会更刺激！

考虑到大部分职业爬虫工程师的爬虫都会部署到服务器，所以ScrapydArt 通过以下几种方式实现了平台的访问权限控制:

* 自定义视图类
* 编写权限验证装饰器
* 配置文件

启用访问权限
--------------------------------

考虑到迁移的成本和一致性，ScrapydArt默认未开启访问权限。

如果你想要开启，只需要到配置文件中

(配置文件通常位于你python环境的包目录下，如/anaconda3/lib/python3.6/scrapydart/default_scrapyd.conf)

的[scrapyd]级别下新增两个参数[auth_username和auth_password]，就像这样::

    [scrapyd]
    eggs_dir    = eggs
    logs_dir    = logs
    http_port   = 6800
    ……
    ……
    auth_username = quinns
    auth_password = quinns7

记得，要在[scapyd]级别下，而不是更下方的[services]级别,要是配置错误，那就尴尬了。


如何使用
----------------------------------


如果你完成了上面的配置，你需要重新启动ScrapydArt服务才能够生效。同时也意味着你的访问权限已经开启。

为了简短一些，在使用时以::

    un  代替 auth_username
    pwd 代替 auth_password

从此，无论你使用GET还是POST，都必须带上对应的用户名(un)和密码(pwd)，否则你将会被它拒之千里之外.

如果你没有提供对应的用户名与密码，你将得到未授权的提示::

    {"status": "error", "message": "You have not obtained the authorization."}

原来Scrapyd的请求示例(HTTP-GET)::

    curl http://localhost:6800

现在ScrapydArt的请求示例(HTTP-GET)::

    curl http://localhost:6800?un=quinns&pwd=quinns7

原来Scrapyd的请求示例(HTTP-GET)::

    curl http://localhost:6800/invokerank.json

现在ScrapydArt的请求示例(HTTP-GET)::

    curl http://localhost:6800/invokerank.json?un=quinns&pwd=quinns7

原来Scrapyd的请求示例(API-GET)::

    curl http://localhost:6800/daemonstatus.json

现在ScrapydArt的请求示例(API-GET)::

    curl http://localhost:6800/daemonstatus.json -d un=quinns -d pwd=quinns7

原来Scrapyd的请求示例(API-POST)::

    curl http://localhost:6800/order.json -d type=order -d order=start_time

现在ScrapydArt的请求示例(API-POST)::

    curl http://localhost:6800/order.json -d type=order -d order=start_time -d un=quinns -d pwd=quinns7

*un: auth_username 用户名. pwd: auth_password 密码.*
