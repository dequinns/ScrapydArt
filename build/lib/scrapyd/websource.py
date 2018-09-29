import os
# custom import in here
from .webtools import file_read


HEADER_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/header.html"
FOOTERS_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/footers.html"
INDEX_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/index.html"
JOBS_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/jobs.html"
FEATURE_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/feature.html"
DOCUMENTS_HTML = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/documents.html"
STYLE_CSS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/css/style.css"
RESET_CSS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/css/reset.css"
JQUERY_JS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/js/jquery-2.1.4.js"
MAIN_JS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/js/main.js"
MODERN_JS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/js/modern.js"
VELOCITY_MIN_JS = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/js/velocity.min.js"
SVG = os.path.dirname(os.path.dirname(__file__)) + "/scrapyd/template/img/cd-icon-arrow.svg"


FILES = [HEADER_HTML, FOOTERS_HTML, INDEX_HTML, JOBS_HTML, FEATURE_HTML,
         DOCUMENTS_HTML, STYLE_CSS, RESET_CSS, JQUERY_JS, MAIN_JS,
         MODERN_JS, VELOCITY_MIN_JS, SVG]


files = list(map(file_read, FILES))


