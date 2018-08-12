#-*- coding:UTF-8 -*-

from setuptools import setup, find_packages
from buptelecmon.version import __version__

setup(name = 'buptelecmon',
    version = __version__,
    description = 'A program for checking electricity charge.',
    long_description = open('README.rst').read(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ], # Get more classifiers from https://pypi.org/pypi?%3Aaction=list_classifiers
    keywords = 'python bupt electricity',
    author = 'jerrymakesjelly',
    author_email = 'ganzhaoyu037@gmail.com',
    url = 'https://github.com/jerrymakesjelly/electricity-monitor',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
    install_requires = [
        'requests',
        'qrcode'
    ],
    entry_points = {
        'console_scripts':[
            'elecinfo = buptelecmon.main:loader'
        ]
    }
)