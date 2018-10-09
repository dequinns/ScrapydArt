import json
from functools import reduce
from datetime import timedelta
from collections import Counter
from datetime import datetime
from copy import copy
import logging

from .webservice import get_spider_list
from .utils import native_stringify_dict


def file_read(filename):
    with open(filename, 'r', encoding="utf-8") as h:
        text_bytes = h.read().encode("utf-8")
        text_str = str(text_bytes, encoding="utf-8")
        return text_str


def str_to_bytes(values):
    if isinstance(values, str):
        return bytes(values, encoding="utf-8")


def bytes_to_str(values):
    if isinstance(values, bytes):
        return str(values, encoding="utf-8")


def format_dict(values):
    if isinstance(values, dict):
        value = json.dumps(values) + "<br/>"
        return value


def get_spiders(values):
    """ 第一次get_spider_list时很费时，大约2s多。但是会放在缓存，后面访问直接从缓存拿，则很快
    [['tips', 'nof'], ['nop']] -> ['tips', 'nof', 'nop']
    """
    if not values:
        return []
    value = list(reduce(lambda x, y: x+y,  map(get_spider_list, values)))  # first 2.8s
    return value


def make_table(values):
    tds = []
    for v in values:
        project_name, spider_name, number = v.get("project"), v.get("spider"), v.get("number")
        aps = "<tr><td><i>{project_name}</i></td><td>{spider_name}</td><td>{spider_num}</td></tr>".format(
            project_name=project_name, spider_name=spider_name, spider_num=number)
        tds.append(aps)
    table = "".join(tds) if len(tds) else ""
    return table


def time_rank(self, index=0):
    """爬虫运行时间排行 从高到低
    :param index: 排行榜数量 为0时默认取全部数据
    :return: 按运行时长排序的排行榜数据
    """
    finished = self.root.launcher.finished
    # 由于dict的键不能重复，但时间作为键是必定会重复的，所以这里将列表的index位置与时间组成tuple作为dict的键
    tps = {(microsec_trunc(f.end_time - f.start_time), i): f.spider for i, f in enumerate(finished)}
    # rps格式 [{"time": time, "spider": spider}, {"time": time, "spider": spider}]
    result = [{"time": str(k[0]), "spider": tps[k]} for k in sorted(tps.keys(), reverse=True)]  # 已排序
    if len(result) == 0:
        result = [{"rank": 0, "spider": "nothing", "time": "00:00:00"}]
    rps = result if index == 0 else result[:index]  # 为0时取所有排行，为int则进行切片
    return rps


def time_ranks_table(self, index=0):
    """爬虫运行时间排行 从高到低
    :param index: 排行榜数量
    :return: 符合排行榜数的<table>表格
    """
    tds = []
    rps = time_rank(self, index=index)
    for i, r in enumerate(rps):
        aps = "<tr><td><i>{key}</i></td><td>{spider}</td><td>{number}</td></tr>".format(
            key=i, spider=r.get("spider"), number=r.get("time"))
        tds.append(aps)
    table = "".join(tds) if len(tds) else ""
    return table


def microsec_trunc(timelike):
    if hasattr(timelike, 'microsecond'):
        ms = timelike.microsecond
    else:
        ms = timelike.microseconds
    return timelike - timedelta(microseconds=ms)


def get_ps(self):
    """获取项目列表与爬虫列表
    :param self:
    :return: projects-项目列表， spiders-爬虫列表
    """
    projects = list(self.root.scheduler.list_projects())
    spiders = get_spiders(projects)
    return projects, spiders


def get_invokes(finishes, spiders):
    """获取已被调用与未被调用的爬虫名称
    :param: finishes 已运行完毕的爬虫列表
    :param: spiders 爬虫列表
    :return: invoked-被调用过的爬虫集合, un_invoked-未被调用的爬虫集合, most_record-被调用次数最多的爬虫名与次数
    """
    invoked = set(i.spider for i in finishes)
    un_invoked = set(spiders).difference(invoked)
    invoked_record = Counter(i.spider for i in finishes)
    most_record = invoked_record.most_common(1)[0] if invoked_record else ("nothing", 0)
    return invoked, un_invoked, most_record


def run_time_stats(finishes):
    """爬虫运行时间统计
    :param finishes: 已行完毕的爬虫列表
    :return: average-平均时间，shortest-最短运行时间， longest-最长运行时间
    """
    runtime = [microsec_trunc(f.end_time - f.start_time) for f in finishes]  # 爬虫运行时间
    # 平均时间, 求和不能用sum, 采用reduce进行计算
    average = reduce(lambda x, y: x + y, runtime) / len(runtime) if runtime else "0:00:00"
    shortest = min(runtime) if runtime else "0:00:00"  # 最短运行时间
    longest = max(runtime) if runtime else "0:00:00"  # 最长运行时间
    return average, shortest, longest


def status_nums(self, finishes):
    """获取当前不同状态的爬虫数
    :param finishes: 已行完毕的爬虫列表
    :return: pending/running/finished状态爬虫数的列表 list
    """
    pends = [queue.list() for project, queue in self.root.poller.queues.items()]
    run_value = self.root.launcher.processes.values()  # 正在运行的爬虫列表
    pend = pends[0] if pends else []
    return list(map(len, [pend, run_value, finishes]))


def get_psn(projects):
    """ 获取项目与对应爬虫的名称及数量
    :param projects: 项目列表
    :return: [{"project": i, "spider": "tip, sms", "number": 2}, {……}] 结果列表
    """
    return [{"project": i, "spider": ",".join(get_spider_list(i)), "number": len(get_spider_list(i))} for i in projects]


def features(self):
    """ 爬虫统计数据 """
    finishes = self.root.launcher.finished
    pending, running, finished = status_nums(self, finishes)  # 待启动/正在运行/已结束爬虫数
    average, shortest, longest = run_time_stats(finishes)  # 爬虫运行时间统计
    ranks = time_ranks_table(self, index=10)  # 爬虫运行时间排行
    projects, spiders = get_ps(self)  # 项目/爬虫列表
    invoked_spider, un_invoked_spider, most_record = get_invokes(finishes, spiders)  # 被调用过/未被调用的爬虫
    lpn, lsn = len(projects), len(spiders)
    pro_spider = get_psn(projects)  # 项目与对应爬虫
    return [pending, running, finished, average, shortest,
            longest, projects, spiders, ranks, pro_spider,
            lpn, lsn, invoked_spider, un_invoked_spider, most_record]


def host_information(request):
    host, port, un, pwd = request.host.host, str(request.host.port), "un", "pwd"
    if request.args.get(bytes(un, encoding="utf-8")) and request.args.get(bytes(pwd, encoding="utf-8")):
        username = str(request.args.get(bytes(un, encoding="utf-8"))[0], encoding="utf-8")
        password = str(request.args.get(bytes(pwd, encoding="utf-8"))[0], encoding="utf-8")
        return {"host": host, "port": port, "un": username, "pwd": password}
    return {"host": host, "port": port, "username": "", "pwd": ""}


def make_urls(hosts):
    urls = []
    for x in ["", "/jobs", "/feature", "/documents"]:
        uri = "?un=%s&pwd=%s" % (hosts.get("un"), hosts.get("pwd"))
        url = "http://" + hosts.get("host") + ":" + hosts.get("port") + x + uri
        urls.append(url)
    return urls


def valid_date(start, end, half="%Y-%m-%d %X"):
    """ 校验时间格式，如果错误则返回False，如果正确则返回格式化后的时间字符串 """
    try:
        start_time, end_time = datetime.strptime(start, half), datetime.strptime(end, half)
        days = (end_time - start_time).days
        if days < 0:
            return False
        return start_time, end_time
    except Exception as err:
        logging.info(err)
        return False


def valid_date_single(value, half="%Y-%m-%d"):
    """ 校验单个时间格式，如果错误则返回False，如果正确则返回格式化后的时间字符串 """
    try:
        date = value.date()
        return datetime.strptime(date, half)
    except Exception:
        return False


def valid_args(request, arg, default={}):
    _types = {"time": ["st", "et"], "project": ["project"], "spider": ["spider"],
              "runtime": ["runtime"], "order": ["order"]}
    if isinstance(arg, str):
        args = native_stringify_dict(copy(request.args), keys_only=False)
        try:
            type_name = args[arg][0]
            if type_name not in _types.keys():
                return default
            try:
                values = _types.get(type_name)
                params = [args[i][0] for i in values]
                res = dict(zip(values, params))
                res["type"] = type_name
                return res
            except Exception as err:
                logging.info(err)
                return default
        except Exception as err:
            logging.info(err)
            return default
    return default


def valid_params(filter_params):
    if not isinstance(filter_params, dict):
        return False
    if not len(filter_params):
        return False
    return True


def valid_index(request, arg, ins=None, default=0):
    _ins = {"str": str, "int": int, "float": float, "list": list, "tuple": tuple, "dict": dict, "set": set}
    if not isinstance(arg, str):
        return default
    args = native_stringify_dict(copy(request.args), keys_only=False)
    try:
        value = args[arg][0]
        if ins not in _ins.keys():
            return value
        ins_type = _ins.get(ins)
        if not isinstance(value, ins_type):
            try:
                return ins_type(value)
            except Exception as err:
                logging.info(err)
                return default
        return value
    except:
        return default


def spider_dict(i):
    aps = {
        "start_time": i.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": i.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "runtime": str(i.end_time - i.start_time),
        "project": i.project,
        "spider": i.spider,
        "logs": i.logfile}
    return aps
