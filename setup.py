#-*- coding:UTF-8 -*-

from setuptools import setup, find_packages
from buptelecmon.version import __version__

setup(name = 'buptelecmon',
    version = __version__,
    description = 'A program for checking electricity charge.',
    long_description = open('README.rst').read(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ], # Get more classifiers from https://pypi.org/pypi?%3Aaction=list_classifiers
    keywords = 'python bupt electricity',
    author = 'jerrymakesjelly',
    author_email = 'ganzhaoyu037@sina.com',
    url = 'https://github.com/jerrymakesjelly/electricity-monitor',
    license = 'GPLv3',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
    install_requires = [
        'enum34',
        'requests'
    ],
    entry_points = {
        'console_scripts':[
            'elecfee = buptelecmon.main:loader'
        ]
    }
)