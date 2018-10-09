import sys

try:
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools = False

from os.path import join, dirname

with open(join(dirname(__file__), 'scrapydart/VERSION')) as f:
    version = f.read().strip()

setup_args = {
    'name': 'scrapydart',
    'version': version,
    'url': 'https://github.com/scrapy/scrapydart',
    'description': 'A service for running Scrapy spiders, with an HTTP API',
    'long_description': open('README.rst', encoding="utf-8").read(),
    'author': 'Scrapy developers',
    'maintainer': 'Scrapy developers',
    'maintainer_email': 'info@scrapy.org',
    'license': 'BSD',
    'packages': ['scrapydart'],
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Internet :: WWW/HTTP',
    ],
}


if using_setuptools:
    setup_args['install_requires'] = [
        'Twisted>=8.0',
        'Scrapy>=1.0',
        'six',
        'enum-compat',
    ]
    setup_args['entry_points'] = {'console_scripts': [
        'scrapydart = scrapydart.scripts.scrapyd_run:main'
    ]}
else:
    setup_args['scripts'] = ['scrapydart/scripts/scrapyd_run.py']

setup(**setup_args)
