from datetime import datetime
import socket
from twisted.web import resource, static
from twisted.application.service import IServiceCollection
from scrapy.utils.misc import load_object
from .interfaces import IPoller, IEggStorage, ISpiderScheduler
from six.moves.urllib.parse import urlparse

from .auth import decorator_auth
from .webservice import CustomResource
from .webtools import str_to_bytes, make_table, microsec_trunc, features, host_information, make_urls
from .websource import files

HEADER_HTML, FOOTERS_HTML, INDEX_HTML, JOBS_HTML, FEATURE_HTML, \
DOCUMENTS_HTML, STYLE_CSS, RESET_CSS, JQUERY_JS, MAIN_JS, \
MODERN_JS, VELOCITY_MIN_JS, SVG = files


class Root(resource.Resource):

    def __init__(self, config, app):
        resource.Resource.__init__(self)
        self.debug = config.getboolean('debug', False)
        self.runner = config.get('runner')
        logsdir = config.get('logs_dir')
        itemsdir = config.get('items_dir')
        local_items = itemsdir and (urlparse(itemsdir).scheme.lower() in ['', 'file'])
        self.app = app
        self.nodename = config.get('node_name', socket.gethostname())
        self.putChild(b'', Home(self, local_items))
        if logsdir:
            self.putChild(b'logs', static.File(logsdir.encode('ascii', 'ignore'), 'text/plain'))
        if local_items:
            self.putChild(b'items', static.File(itemsdir, 'text/plain'))
        self.putChild(b'jobs', Jobs(self, local_items))
        self.putChild(b'feature', Feature(self, local_items))
        services = config.items('services', ())
        for servName, servClsName in services:
            servCls = load_object(servClsName)
            self.putChild(servName.encode('utf-8'), servCls(self))
        self.update_projects()

    def update_projects(self):
        self.poller.update_projects()
        self.scheduler.update_projects()

    @property
    def launcher(self):
        app = IServiceCollection(self.app, self.app)
        return app.getServiceNamed('launcher')

    @property
    def scheduler(self):
        return self.app.getComponent(ISpiderScheduler)

    @property
    def eggstorage(self):
        return self.app.getComponent(IEggStorage)

    @property
    def poller(self):
        return self.app.getComponent(IPoller)


class Home(CustomResource):
    """ 继承JsonResource方法以实现decorator_auth能够返回json格式数据  """

    def __init__(self, root, local_items):
        resource.Resource.__init__(self)
        self.root = root
        self.local_items = local_items

    @decorator_auth
    def render_GET(self, request):
        pending, running, finished, average, shortest, \
        longest, projects, spiders, ranks, dps, \
        lpn, lsn, invoked_spider, un_invoked_spider, most_record = features(self)

        table = make_table(dps)
        hosts = host_information(request)  # host以及auth信息
        home_uri, jobs_uri, feature_uri, documents_uri = make_urls(hosts)

        nav = """
                <ul>
                <li>
                <a href={home_uri} class="selected" id="home">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polygon fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points="12,2 3,10 3,23 9,23 9,16 15,16 15,23 21,23 21,10 " stroke-linejoin="miter"></polygon> </g></svg>
                Home</a>
                </li>
                <li>
                <a href={jobs_uri} class="item" id="jobs">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polyline data-color="color-2" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points=" 16,7 16,2 8,2 8,7 " stroke-linejoin="miter"></polyline> <rect x="1" y="7" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="15" stroke-linejoin="miter"></rect> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="5" y1="7" x2="5" y2="22" stroke-linejoin="miter"></line> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="19" y1="7" x2="19" y2="22" stroke-linejoin="miter"></line> </g></svg>
                Jobs</a>
                </li>
                <li>
                <a href={feature_uri} class="item" id="feature">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <rect x="1" y="1" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="22" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> </g></svg>
                ArtDoc</a>
                </li>

                
                </ul>
                    """.format(home_uri=home_uri, jobs_uri=jobs_uri, feature_uri=feature_uri,
                               documents_uri=documents_uri)
        header = HEADER_HTML.format(style_css=STYLE_CSS, reset_css=RESET_CSS, nav=nav)

        index = INDEX_HTML.format(projects=dps, nop=pending, nor=running, nof=finished, average=average,
                                  shortest=shortest, longest=longest, lpn=lpn, lsn=lsn, most_spider=most_record[0],
                                  most_num=most_record[1], invoked_spider=",".join(invoked_spider),
                                  un_invoked_spider=",".join(un_invoked_spider), table=table, ranks=ranks,
                                  feature_uri=feature_uri)
        footers = FOOTERS_HTML
        self.content = str_to_bytes(header + index + footers)  # return value need bytes
        return self.content


class Jobs(CustomResource):

    def __init__(self, root, local_items):
        resource.Resource.__init__(self)
        self.root = root
        self.local_items = local_items

    cancel_button = """
    <form method="post" action="/cancel.json">
    <input type="hidden" name="project" value="{project}"/>
    <input type="hidden" name="job" value="{jobid}"/>
    <input type="submit" style="float: left;" value="Cancel"/>
    </form>
    """.format

    header_cols = [
        'Project', 'Spider', 'Job', 'PID', 'Start',
        'Runtime', 'Finish', 'Log', 'Items', 'Cancel',
    ]

    def prep_table(self):
        finished_res = self.prep_tab_finished()
        finished, f_num = finished_res.get("finished"), finished_res.get("number")
        running_res = self.prep_tab_running()
        running, r_num = running_res.get("running"), running_res.get("number")
        pending_res = self.prep_tab_pending()
        pending, p_num = pending_res.get("pending"), pending_res.get("number")
        return (
                '<tbody>'
                + '<tr><td colspan="%d"><span style="font-size:16px;">Pending:</span>' % len(
            self.header_cols) + "\t" + p_num + '</td></tr>'
                + pending +
                '</tbody>'
                '<tbody>'
                + '<tr><td colspan="%d"><span style="font-size:16px;">Running:</span>' % len(
            self.header_cols) + "\t" + r_num + '</td></tr>'
                + running +
                '</tbody>'
                '<tbody>'
                + '<tr><td colspan="%d"><span style="font-size:16px;">Finished:</span>' % len(
            self.header_cols) + "\t" + f_num + '</td></tr>'
                + finished +
                '</tbody>'
        )

    def prep_tab_pending(self):
        pending = '\n'.join(
            self.prep_row(dict(
                Project=project, Spider=m['name'], Job=m['_job'],
                Cancel=self.cancel_button(project=project, jobid=m['_job'])
            ))
            for project, queue in self.root.poller.queues.items()
            for m in queue.list()
        )
        quinn = [queue.list() for project, queue in self.root.poller.queues.items()]
        dps = len(quinn[0]) if quinn else 0  # quinn格式为[[{}, {}, {}]]
        return {"pending": pending, "number": str(dps)}

    def prep_tab_running(self):
        running = '\n'.join(
            self.prep_row(dict(
                Project=p.project, Spider=p.spider,
                Job=p.job, PID=p.pid,
                Start=microsec_trunc(p.start_time),
                Runtime=microsec_trunc(datetime.now() - p.start_time),
                Log='<a href="/logs/%s/%s/%s.log">Log</a>' % (p.project, p.spider, p.job),
                Items='<a href="/items/%s/%s/%s.jl">Items</a>' % (p.project, p.spider, p.job),
                Cancel=self.cancel_button(project=p.project, jobid=p.job)
            ))
            for p in self.root.launcher.processes.values()
        )
        dps = len(self.root.launcher.processes.values())
        return {"running": running, "number": str(dps)}

    def prep_tab_finished(self):
        finished = "\n".join(
            self.prep_row(dict(
                Project=p.project, Spider=p.spider,
                Job=p.job,
                Start=microsec_trunc(p.start_time),
                Runtime=microsec_trunc(p.end_time - p.start_time),
                Finish=microsec_trunc(p.end_time),
                Log='<a href="/logs/%s/%s/%s.log">Log</a>' % (p.project, p.spider, p.job),
                Items='<a href="/items/%s/%s/%s.jl">Items</a>' % (p.project, p.spider, p.job),
            ))
            for p in self.root.launcher.finished
        )
        dps = len(self.root.launcher.finished)
        return {"finished": finished, "number": str(dps)}

    def prep_header(self, cells):
        """ 构造表头并加上html标签 """
        if not isinstance(cells, dict):
            assert len(cells) == len(self.header_cols)
        else:
            cells = [cells.get(k) for k in self.header_cols]
        cells = ['<th style="font-size: 16px;">%s</th>' % ('' if c is None else c) for c in cells]
        return '<tr>%s</tr>' % ''.join(cells)

    def prep_row(self, cells):
        if not isinstance(cells, dict):
            assert len(cells) == len(self.header_cols)
        else:
            cells = [cells.get(k) for k in self.header_cols]
        cells = ['<td>%s</td>' % ('' if c is None else c) for c in cells]
        return '<tr>%s</tr>' % ''.join(cells)

    @decorator_auth
    def render_GET(self, request):
        table_header = self.prep_header(self.header_cols)

        pending, running, finished, average, shortest, \
        longest, projects, spiders, ranks, dps, \
        lpn, lsn, invoked_spider, un_invoked_spider, most_record = features(self=self)

        hosts = host_information(request)  # host以及auth信息
        home_uri, jobs_uri, feature_uri, documents_uri = make_urls(hosts)
        nav = """
        <ul>
        <li>
        <a href={home_uri} class="item" id="home">
        <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polygon fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points="12,2 3,10 3,23 9,23 9,16 15,16 15,23 21,23 21,10 " stroke-linejoin="miter"></polygon> </g></svg>
        Home</a>
        </li>
        <li>
        <a href={jobs_uri} class="selected" id="jobs">
        <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polyline data-color="color-2" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points=" 16,7 16,2 8,2 8,7 " stroke-linejoin="miter"></polyline> <rect x="1" y="7" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="15" stroke-linejoin="miter"></rect> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="5" y1="7" x2="5" y2="22" stroke-linejoin="miter"></line> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="19" y1="7" x2="19" y2="22" stroke-linejoin="miter"></line> </g></svg>
        Jobs</a>
        </li>
        <li>
        <a href={feature_uri} class="item" id="feature">
        <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <rect x="1" y="1" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="22" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> </g></svg>
        ArtDoc</a>
        </li>

        </ul>
            """.format(home_uri=home_uri, jobs_uri=jobs_uri, feature_uri=feature_uri, documents_uri=documents_uri)
        header = HEADER_HTML.format(style_css=STYLE_CSS, reset_css=RESET_CSS, nav=nav)
        most_spider, most_num = most_record
        feature_uri = feature_uri

        jobs = JOBS_HTML.format(table_header=table_header, tables=self.prep_table(), most_spider=most_spider,
                                most_num=most_num, invoked_spider=",".join(invoked_spider),
                                un_invoked_spider=",".join(un_invoked_spider), feature_uri=feature_uri)
        footers = FOOTERS_HTML
        self.content = str_to_bytes(header + jobs + footers)  # return value need bytes
        return self.content


class Feature(CustomResource):

    def __init__(self, root, local_items):
        resource.Resource.__init__(self)
        self.root = root
        self.local_items = local_items

    @decorator_auth
    def render_GET(self, request):
        hosts = host_information(request)  # host以及auth信息
        home_uri, jobs_uri, feature_uri, documents_uri = make_urls(hosts)
        nav = """
                <ul>
                <li>
                <a href={home_uri} class="item" id="home">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polygon fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points="12,2 3,10 3,23 9,23 9,16 15,16 15,23 21,23 21,10 " stroke-linejoin="miter"></polygon> </g></svg>
                Home</a>
                </li>
                <li>
                <a href={jobs_uri} class="item" id="jobs">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <polyline data-color="color-2" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" points=" 16,7 16,2 8,2 8,7 " stroke-linejoin="miter"></polyline> <rect x="1" y="7" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="15" stroke-linejoin="miter"></rect> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="5" y1="7" x2="5" y2="22" stroke-linejoin="miter"></line> <line fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" x1="19" y1="7" x2="19" y2="22" stroke-linejoin="miter"></line> </g></svg>
                Jobs</a>
                </li>
                <li>
                <a href={feature_uri} class="selected" id="feature">
                <svg class="nc-icon outline" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px" viewBox="0 0 24 24"><g transform="translate(0, 0)"> <rect x="1" y="1" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="22" height="22" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="5" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="5" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> <rect data-color="color-2" x="14" y="14" fill="none" stroke="#4a5261" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" width="5" height="5" stroke-linejoin="miter"></rect> </g></svg>
                ArtDoc</a>
                </li>

                </ul>
                    """.format(home_uri=home_uri, jobs_uri=jobs_uri, feature_uri=feature_uri,
                               documents_uri=documents_uri)
        header = HEADER_HTML.format(style_css=STYLE_CSS, reset_css=RESET_CSS, nav=nav)

        feature = FEATURE_HTML.format()
        footers = FOOTERS_HTML
        self.content = str_to_bytes(header + feature + footers)  # return value need bytes
        return self.content
