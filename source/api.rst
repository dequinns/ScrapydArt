.. _api:

API
===

Scrapyd原有 API 保留，这里列出新增加的API资源及信息


schedulelist.json
-----------------

用于获取爬虫调用情况,如::

    invoked_spider - 被调用过的爬虫

    un_invoked_spider - 未被调用过的爬虫

    most_record - 被调用次数最多的爬虫名称及次数

* 支持的请求方式: ``GET``

请求示例::

    curl http://localhost:6800/schedulelist.json

响应示例::

    {"node_name": "node-name", "status": "ok", "invoked_spider": ["tips", "smtb"], "un_invoked_spider": ["lagou"], "most_record": ["tips", 3]}




runtimestats.json
---------------

爬虫运行时间统计,如::

    average - 所有爬虫的平均运行时长

    shortest - 爬虫运行的最短时间

    longest - 爬虫运行的最长时间

* 支持的请求方式: ``GET``

请求示例::

    curl http://localhost:6800/runtimestats.json

响应示例::

    {"node_name": "node-name", "status": "ok", "average": "0:00:04", "shortest": "0:00:01", "longest": "0:00:12"}



psnstats.json
-------------

项目及爬虫数量统计,如::

    project_nums - 项目总数

    spider_nums - 爬虫总数

* 支持的请求方式: ``GET``

请求示例::

    curl http://localhost:6800/psnstats.json

响应示例::

    {"node_name": "node-name", "status": "ok", "project_nums": 2, "spider_nums": 3}


prospider.json
-------------

项目与对应爬虫名以及数量统计,如::

    pro_spider - 结果集

        project - 项目名称

        spider - 项目对应的爬虫名称

* 支持的请求方式: ``GET``

请求示例::

    curl http://localhost:6800/prospider.json

响应示例::

    {"node_name": "node-name", "status": "ok", "pro_spider": [{"project": "Lagous", "spider": "lagou,tips", "number": 2}, {"project": "smtaobao", "spider": "smtb", "number": 1}]}


timerank.json
-------------

爬虫运行时长榜,如::

    ranks - 结果集

        time - 运行时长

        spider - 项目对应的爬虫名称

* 支持的请求方式: ``GET``
* 参数:

  * ``index`` (int, 可选参数) - 排行榜默认取前10条记录，你可以通过index来指定想要的记录数量

请求示例::

    curl http://localhost:6800/timerank.json?index=5

响应示例::

    {"node_name": "node-name", "status": "ok",
    "ranks":[
        {"time": "0:00:52", "spider": "dps"},
        {"time": "0:00:33", "spider": "invorank"},
        {"time": "0:00:18", "spider": "lagou"},
        {"time": "0:00:10", "spider": "smtb"},
        {"time": "0:00:02", "spider": "tips"}
    ]}



invokerank.json
-------------

爬虫调用排行榜,如::

    ranks - 结果集

* 支持的请求方式: ``GET``
* 参数:

  * ``index`` (int, 可选参数) - 排行榜默认取前10条记录，你可以通过index来指定想要的记录数量

请求示例::

    curl http://localhost:6800/invokerank.json?index=5

响应示例::

    {"node_name": "node-name", "status": "ok",
    "ranks":[
        ["tips", 5],
        ["lagou", 5],
        ["smtb", 4]
    ]}


.. note:: [奎因W提示] 下面的API请求方式都是POST方式，参数较多，需要仔细看清文档。编写文档时我都是边测边写，所以文档的参数及用法是通过测试的。


filter.json
---------------

根据参数按时间范围/项目名称/爬虫名称/运行时长对爬虫运行记录进行筛选过滤。

* 支持的请求方式: ``POST``
* 参数:

  * ``index`` (int, 可选) - 记录条数， 默认10条。

  * ``type`` (string, 不可选) - 过滤类型，可选类型参数为：time/project/spider/runtime,以下为每个类型的对应参数

    * ``time`` (string, 参数： st, et) - 时间范围，如2018-09-26 00:00:00, 2018-09-30 18:30:00

    * ``project`` (string, 参数： project) - 项目名称，如:Alibaba

    * ``spider`` (string, 参数： spider) - 爬虫名称，如:tmall

    * ``runtime`` (int, 参数： runtime) - 运行时长(秒)，如:5

      * ``compare`` (sting, 参数： greater/less/equal/greater equal/less equal) - 比较运算，如:greater（大于）、less(小于)、equal(等于)、greater equal(大于等于)、less equal(小于等于)


时间范围筛选(time)请求示例::

    $ curl http://localhost:6800/filter.json -d type=time -d st=2018-09-26 00:00:00 -d et=2018-09-30 18:30:00 -d index=5

*st: start_time 爬虫启动时间. et: end_time 爬虫结束时间.*

时间范围筛选(time)响应示例::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
              "start_time": "2018-09-30 09:34:08",
              "end_time": "2018-09-30 09:34:16",
              "runtime": "0:00:08.266556",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ea5107d6c45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:13",
              "end_time": "2018-09-30 09:34:21",
              "runtime": "0:00:07.874961",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ebccab4cc45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:18",
              "end_time": "2018-09-30 09:34:26",
              "runtime": "0:00:08.072063",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ec4d03d2c45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:23",
              "end_time": "2018-09-30 09:34:30",
              "runtime": "0:00:07.029813",
              "project": "Lagous",
              "spider": "lagou",
              "logs": "logs/Lagous/lagou/f17c0dc6c45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:28",
              "end_time": "2018-09-30 09:34:36",
              "runtime": "0:00:07.774142",
              "project": "Lagous",
              "spider": "lagou",
              "logs": "logs/Lagous/lagou/f33211d8c45011e8970954ee75c0e204.log"
          }
      ]
      }


指定项目筛选(project)请求示例::

    $ curl http://localhost:6800/filter.json -d type=project -d project=Lagous -d index=3

*project: project name 爬虫项目名称.*

指定项目筛选(project)响应示例::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
              "start_time": "2018-09-30 09:34:08",
              "end_time": "2018-09-30 09:34:16",
              "runtime": "0:00:08.266556",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ea5107d6c45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:13",
              "end_time": "2018-09-30 09:34:21",
              "runtime": "0:00:07.874961",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ebccab4cc45011e8970954ee75c0e204.log"
          },
          {
              "start_time": "2018-09-30 09:34:18",
              "end_time": "2018-09-30 09:34:26",
              "runtime": "0:00:08.072063",
              "project": "Lagous",
              "spider": "tips",
              "logs": "logs/Lagous/tips/ec4d03d2c45011e8970954ee75c0e204.log"
          }
      ]
      }



指定爬虫名称筛选(spider)请求示例::

    $ curl http://localhost:6800/filter.json -d type=spider -d spider=tips

*spider: spider name 爬虫项目名称.*

指定爬虫名称筛选(spider)响应示例::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
            "start_time": "2018-09-30 09:34:13",
            "end_time": "2018-09-30 09:34:21",
            "runtime": "0:00:07.874961",
            "project": "Lagous",
            "spider": "tips",
            "logs": "logs/Lagous/tips/ebccab4cc45011e8970954ee75c0e204.log"
        },
        {
            "start_time": "2018-09-30 09:34:18",
            "end_time": "2018-09-30 09:34:26",
            "runtime": "0:00:08.072063",
            "project": "Lagous",
            "spider": "tips",
            "logs": "logs/Lagous/tips/ec4d03d2c45011e8970954ee75c0e204.log"
        }
      ]
      }



指定爬虫运行时长筛选(runtime)请求示例(greater)::

    $ curl http://localhost:6800/filter.json -d type=runtime -d runtime=8 -d compare=greater

*spider: spider name 爬虫项目名称. runtime : runtime 运行时间. compare: compare 数学运算类型*

指定爬虫运行时长筛选(runtime)响应示例(greater)::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
            "start_time": "2018-09-30 09:34:38",
            "end_time": "2018-09-30 09:34:55",
            "runtime": "0:00:16.977073",
            "project": "Lagous",
            "spider": "waper",
            "logs": "logs/Lagous/waper/fbcb5ad4c45011e8970954ee75c0e204.log"
        }
      ]
      }


指定爬虫运行时长筛选(runtime)请求示例(less)::

    $ curl http://localhost:6800/filter.json -d type=runtime -d runtime=8 -d compare=less

*spider: spider name 爬虫项目名称. runtime : runtime 运行时间. compare: compare 数学运算类型*

指定爬虫运行时长筛选(runtime)响应示例(less)::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
            "start_time": "2018-09-30 09:34:23",
            "end_time": "2018-09-30 09:34:30",
            "runtime": "0:00:07.029813",
            "project": "Lagous",
            "spider": "lagou",
            "logs": "logs/Lagous/lagou/f17c0dc6c45011e8970954ee75c0e204.log"
        },
        {
            "start_time": "2018-09-30 09:34:28",
            "end_time": "2018-09-30 09:34:36",
            "runtime": "0:00:07.774142",
            "project": "Lagous",
            "spider": "lagou",
            "logs": "logs/Lagous/lagou/f33211d8c45011e8970954ee75c0e204.log"
        }
      ]
      }



order.json
---------------

根据参数按时间范围/项目名称/爬虫名称/运行时长对爬虫运行记录进行筛选过滤。

* 支持的请求方式: ``POST``
* 参数:

  * ``index`` (int, 可选) - 记录条数， 默认10条。

  * ``reverse`` (int, 可选(0 or 1)) - 记录条数， 默认为0，即升序。

  * ``order`` (string, 不可选) - 排序key，可用参数为：start_time/end_time/spider/project/runtime


排序请求示例(start_time, 默认升序)::

    $ curl http://localhost:6800/order.json -d type=order -d order=start_time

*start_time: start_time 爬虫启动时间.*

排序响应示例(start_time, 默认升序)::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
           "start_time": "2018-09-30 09:34:08",
           "end_time": "2018-09-30 09:34:16",
           "runtime": "0:00:08.266556",
           "project": "Lagous",
           "spider": "tips",
           "logs": "logs/Lagous/tips/ea5107d6c45011e8970954ee75c0e204.log"
       },
       {
           "start_time": "2018-09-30 09:34:13",
           "end_time": "2018-09-30 09:34:21",
           "runtime": "0:00:07.874961",
           "project": "Lagous",
           "spider": "tips",
           "logs": "logs/Lagous/tips/ebccab4cc45011e8970954ee75c0e204.log"
       }
      ]
      }


排序请求示例(start_time, 指定降序)::

    $ curl http://localhost:6800/order.json -d type=order -d order=start_time -d reverse=1

*start_time: start_time 爬虫启动时间.*

排序响应示例(start_time, 指定降序)::

      {
      "node_name": "node-name",
      "status": "ok",
      "spider": [
          {
            "start_time": "2018-09-30 09:34:43",
            "end_time": "2018-09-30 09:35:00",
            "runtime": "0:00:17.017967",
            "project": "Lagous",
            "spider": "waper",
            "logs": "logs/Lagous/waper/fc37e708c45011e8970954ee75c0e204.log"
        },
        {
            "start_time": "2018-09-30 09:34:38",
            "end_time": "2018-09-30 09:34:55",
            "runtime": "0:00:16.977073",
            "project": "Lagous",
            "spider": "waper",
            "logs": "logs/Lagous/waper/fbcb5ad4c45011e8970954ee75c0e204.log"
        }
      ]
      }
