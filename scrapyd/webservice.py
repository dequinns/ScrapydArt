from copy import copy
import traceback
import uuid
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from twisted.python import log
from datetime import datetime
from collections import Counter

from .utils import get_spider_list, JsonResource, UtilsCache, native_stringify_dict
from twisted.web import resource
from .auth import decorator_auth
from .webtools import get_invokes, get_ps, run_time_stats, get_psn, microsec_trunc
from .webtools import valid_date, valid_index, valid_args, valid_params, spider_dict


class WsResource(JsonResource):

    def __init__(self, root):
        JsonResource.__init__(self)
        self.root = root

    def render(self, txrequest):
        try:
            return JsonResource.render(self, txrequest).encode('utf-8')
        except Exception as e:
            if self.root.debug:
                return traceback.format_exc().encode('utf-8')
            log.err()
            r = {"node_name": self.root.nodename, "status": "error", "message": str(e)}
            return self.render_object(r, txrequest).encode('utf-8')


class CustomResource(JsonResource, resource.Resource):

    def __init__(self, root):
        JsonResource.__init__(self)
        self.root = root

    def render(self, txrequest):
        try:
            return JsonResource.render(self, txrequest).encode('utf-8')
        except Exception:
            return self.content


class DaemonStatus(WsResource):
    @decorator_auth
    def render_GET(self, txrequest):
        pending = sum(q.count() for q in self.root.poller.queues.values())
        running = len(self.root.launcher.processes)
        finished = len(self.root.launcher.finished)

        return {"node_name": self.root.nodename, "status": "ok", "pending": pending, "running": running, "finished": finished}


class Schedule(WsResource):

    @decorator_auth
    def render_POST(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        settings = args.pop('setting', [])
        settings = dict(x.split('=', 1) for x in settings)
        args = dict((k, v[0]) for k, v in args.items())
        project = args.pop('project')
        spider = args.pop('spider')
        version = args.get('_version', '')
        spiders = get_spider_list(project, version=version)
        if not spider in spiders:
            return {"status": "error", "message": "spider '%s' not found" % spider}
        args['settings'] = settings
        jobid = args.pop('jobid', uuid.uuid1().hex)
        args['_job'] = jobid
        self.root.scheduler.schedule(project, spider, **args)
        return {"node_name": self.root.nodename, "status": "ok", "jobid": jobid}


class Cancel(WsResource):
    @decorator_auth
    def render_POST(self, txrequest):
        args = dict((k, v[0])
                    for k, v in native_stringify_dict(copy(txrequest.args),
                                    keys_only=False).items())
        project = args['project']
        jobid = args['job']
        signal = args.get('signal', 'TERM')
        prevstate = None
        queue = self.root.poller.queues[project]
        c = queue.remove(lambda x: x["_job"] == jobid)
        if c:
            prevstate = "pending"
        spiders = self.root.launcher.processes.values()
        for s in spiders:
            if s.job == jobid:
                s.transport.signalProcess(signal)
                prevstate = "running"
        return {"node_name": self.root.nodename, "status": "ok", "prevstate": prevstate}


class AddVersion(WsResource):
    @decorator_auth
    def render_POST(self, txrequest):
        project = txrequest.args[b'project'][0].decode('utf-8')
        version = txrequest.args[b'version'][0].decode('utf-8')
        eggf = BytesIO(txrequest.args[b'egg'][0])
        self.root.eggstorage.put(eggf, project, version)
        spiders = get_spider_list(project, version=version)
        self.root.update_projects()
        UtilsCache.invalid_cache(project)
        return {"node_name": self.root.nodename, "status": "ok", "project": project, "version": version, \
            "spiders": len(spiders)}


class ListProjects(WsResource):
    @decorator_auth
    def render_GET(self, txrequest):
        projects = list(self.root.scheduler.list_projects())
        return {"node_name": self.root.nodename, "status": "ok", "projects": projects}


class ListVersions(WsResource):
    @decorator_auth
    def render_GET(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        project = args['project'][0]
        versions = self.root.eggstorage.list(project)
        return {"node_name": self.root.nodename, "status": "ok", "versions": versions}


class ListSpiders(WsResource):
    @decorator_auth
    def render_GET(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        project = args['project'][0]
        version = args.get('_version', [''])[0]
        spiders = get_spider_list(project, runner=self.root.runner, version=version)
        return {"node_name": self.root.nodename, "status": "ok", "spiders": spiders}


class ListJobs(WsResource):
    @decorator_auth
    def render_GET(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        project = args.get('project', [None])[0]
        spiders = self.root.launcher.processes.values()
        queues = self.root.poller.queues
        pending = [
            {"project": project, "spider": x["name"], "id": x["_job"]}
            for qname in (queues if project is None else [project])
            for x in queues[qname].list()
        ]
        running = [
            {
                "project": project,
                "spider": s.spider,
                "id": s.job, "pid": s.pid,
                "start_time": str(s.start_time),
            } for s in spiders if project is None or s.project == project
        ]
        finished = [
            {
                "project": project,
                "spider": s.spider, "id": s.job,
                "start_time": str(s.start_time),
                "end_time": str(s.end_time)
            } for s in self.root.launcher.finished
            if project is None or s.project == project
        ]
        return {"node_name": self.root.nodename, "status": "ok",
                "pending": pending, "running": running, "finished": finished}


class DeleteProject(WsResource):
    @decorator_auth
    def render_POST(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        project = args['project'][0]
        self._delete_version(project)
        UtilsCache.invalid_cache(project)
        return {"node_name": self.root.nodename, "status": "ok"}

    def _delete_version(self, project, version=None):
        self.root.eggstorage.delete(project, version)
        self.root.update_projects()


class DeleteVersion(DeleteProject):
    @decorator_auth
    def render_POST(self, txrequest):
        args = native_stringify_dict(copy(txrequest.args), keys_only=False)
        project = args['project'][0]
        version = args['version'][0]
        self._delete_version(project, version)
        UtilsCache.invalid_cache(project)
        return {"node_name": self.root.nodename, "status": "ok"}


class ScheduleList(WsResource):
    @decorator_auth
    def render_GET(self, request):
        """爬虫调用情况
        如被调用过的爬虫、未被调用过的爬虫、被调用次数最多的爬虫名称及次数
        """
        finishes = self.root.launcher.finished
        projects, spiders = get_ps(self)  # 项目/爬虫列表
        invoked_spider, un_invoked_spider, most_record = get_invokes(finishes, spiders)  # 被调用过/未被调用的爬虫
        return {"node_name": self.root.nodename, "status": "ok", "invoked_spider": list(invoked_spider),
                "un_invoked_spider": list(un_invoked_spider), "most_record": most_record}


class RunTimeStats(WsResource):
    @decorator_auth
    def render_GET(self, request):
        """爬虫运行时间统计
        如平均运行时长、最短运行时间、最长运行时间
        """
        finishes = self.root.launcher.finished
        average, shortest, longest = list(map(str, run_time_stats(finishes)))
        return {"node_name": self.root.nodename, "status": "ok", "average": average,
                "shortest": shortest, "longest": longest}


class PsnStats(WsResource):
    @decorator_auth
    def render_GET(self, request):
        """ 项目及爬虫数量统计,如项目总数、爬虫总数 """
        project_nums, spider_nums = list(map(len, get_ps(self)))
        node_name = self.root.nodename
        return {"node_name": node_name, "status": "ok", "project_nums": project_nums, "spider_nums": spider_nums}


class ProSpider(WsResource):
    @decorator_auth
    def render_GET(self, request):
        """ 项目与对应爬虫名及爬虫数量,如[{"project": i, "spider": "tip, sms", "number": 2}, {……}] """
        projects, spiders = get_ps(self)  # 项目/爬虫列表
        pro_spider = get_psn(projects)  # 项目与对应爬虫
        return {"node_name": self.root.nodename, "status": "ok", "pro_spider": pro_spider}


class TimeRank(WsResource):
    """ 爬虫运行时长排行,根据index参数进行切片 """

    def time_rank(self, index=0):
        """爬虫运行时间排行 从高到低
        :param index: 排行榜数量 默认返回全部数据，index存在时则切片后返回
        :return: 按运行时长排序的排行榜数据 [{"time": time, "spider": spider}, {}]
        """
        finished = self.root.launcher.finished
        # 由于dict的键不能重复，但时间作为键是必定会重复的，所以这里将列表的index位置与时间组成tuple作为dict的键
        tps = {(microsec_trunc(f.end_time - f.start_time), i): f.spider for i, f in enumerate(finished)}
        result = [{"time": str(k[0]), "spider": tps[k]} for k in sorted(tps.keys(), reverse=True)]  # 已排序
        ranks = result if not index else result[:index]
        return ranks

    @decorator_auth
    def render_GET(self, request):
        index = int(valid_index(request=request, arg="index", ins="int", default=10))
        ranks = self.time_rank(index=index)  # 项目/爬虫列表
        return {"node_name": self.root.nodename, "status": "ok", "ranks": ranks}


class InvokeRank(WsResource):
    """ 爬虫运行时长排行 根据index参数进行切片 """

    def _invoke_rank(self, finishes, index=10):
        """获取爬虫被调用次数排行
        :param: finishes 已运行完毕的爬虫列表
        :param: spiders 爬虫列表
        :return: ranks-降序排序的爬虫调用次数列表 [("tip", 3), ()]
        """
        invoked_record = Counter(i.spider for i in finishes)
        ranks = invoked_record.most_common(index) if invoked_record else []
        return ranks

    @decorator_auth
    def render_GET(self, request):
        index = int(valid_index(request=request, arg="index", ins="int", default=10))
        ranks = self._invoke_rank(self.root.launcher.finished, index=index)  # 项目/爬虫列表
        return {"node_name": self.root.nodename, "status": "ok", "ranks": ranks}


class Filter(WsResource):

    def _filter_time(self, filter_params, finishes, request, index, default=[]):
        if not valid_params(filter_params):
            return default
        res = valid_date(filter_params.get("st"), filter_params.get("et"))
        if not res:
            return default
        st, et = res
        spiders = [spider_dict(i) for i in finishes if (i.start_time - st).days >= 0 and (et - i.start_time).days >= 0][:index]
        return spiders

    def _filter_project(self, filter_params, finishes, request, index, default=[]):
        if not valid_params(filter_params):
            return default
        project_name = filter_params.get("project")
        spiders = [spider_dict(i) for i in finishes if i.project == project_name][:index]
        return spiders

    def _filter_spider(self, filter_params, finishes, request, index, default=[]):
        if not valid_params(filter_params):
            return default
        spider_name = filter_params.get("spider")
        spiders = [spider_dict(i) for i in finishes if i.spider == spider_name][:index]
        return spiders

    def _filter_runtime(self, request, filter_params, finishes, index, default=[]):
        runtime = int(valid_index(request, arg="runtime", ins="int", default=None))
        _compare = {
            "greater": lambda x: (x.end_time-x.start_time).seconds > runtime,
            "less": lambda x: (x.end_time-x.start_time).seconds < runtime,
            "equal": lambda x: (x.end_time-x.start_time).seconds == runtime,
            "greater equal": lambda x: (x.end_time-x.start_time).seconds >= runtime,
            "less equal": lambda x: (x.end_time-x.start_time).seconds <= runtime
        }
        args = native_stringify_dict(copy(request.args), keys_only=False)
        compare = args["compare"][0]
        if not valid_params(filter_params) or compare not in _compare.keys() or not runtime:
            return default
        ordered = list(filter(_compare.get(compare), finishes))
        spiders = [spider_dict(i) for i in ordered[:index]]
        return spiders

    @decorator_auth
    def render_POST(self, request):
        """ 根据传入的参数不同，对爬虫运行记录进行排序
        目前支持按时间范围、按爬虫名称、按项目名称、按运行时长进行排序，index默认10
        取出筛选类型、计算并取出类型对应参数以及index参数，并对其进行校验
        根据index进行切片
        :return 符合名称的爬虫信息列表 [{}, {}]
        """
        finishes = self.root.launcher.finished
        types_func = {"time": self._filter_time, "project": self._filter_project,
                      "spider": self._filter_spider, "runtime": self._filter_runtime}
        index = int(valid_index(request=request, arg="index", ins="int", default=10))
        filter_params = valid_args(request=request, arg="type")
        filter_type = filter_params.get("type")
        if filter_type in types_func.keys():
            funcs = types_func.get(filter_type)
            if funcs:
                spiders = funcs(filter_params=filter_params, finishes=finishes, request=request, index=index)
                return {"node_name": self.root.nodename, "status": "ok", "spider": spiders}
        return {"node_name": self.root.nodename, "status": "error", "message": "query parameter error"}


class Order(WsResource):

    @decorator_auth
    def render_POST(self, request):
        """ 根据传入的参数不同，对爬虫运行记录进行排序
        目前支持按启动时间、按结束时间、按项目名称、按爬虫名称以及运行时长进行筛选过滤，index默认10
        计算并取出排序对应参数以及index参数，并对其进行校验
        根据index进行切片
        :return 符合名称的爬虫信息列表 [{}, {}]
        """
        finishes = self.root.launcher.finished
        orders = {
            "start_time": lambda x: x.start_time, "end_time": lambda x: x.end_time,
            "spider": lambda x: x.spider, "project": lambda x: x.project,
            "runtime": lambda x: x.end_time-x.start_time
        }
        index = int(valid_index(request=request, arg="index", ins="int", default=10))
        params = valid_args(request=request, arg="type")
        order_key = params.get(params.get("type"))
        reverse_param = int(valid_index(request=request, arg="reverse", ins="int", default=0))
        if order_key not in orders.keys() or reverse_param not in [0, 1]:
            return {"node_name": self.root.nodename, "status": "error", "message": "query parameter error"}
        ordered = sorted(finishes, key=orders.get(order_key), reverse=reverse_param)
        spiders = [spider_dict(i) for i in ordered[:index]]
        return {"node_name": self.root.nodename, "status": "ok", "spider": spiders}

