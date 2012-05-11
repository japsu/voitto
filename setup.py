#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='voitto',
    version='0.0.1',
    description='A simple yet efficient double ledger',
    long_description=read('README.rst'),
    license='GPLv3+',
    author='Santtu Pajukanta',
    author_email='santtu@pajukanta.fi',
    url='http://github.com/japsu/voitto',
    packages = find_packages(),
    classifiers="""
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: End Users/Desktop
Intended Audience :: Financial and Insurance Industry
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Natural Language :: English
Natural Language :: Finnish
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Topic :: Office/Business :: Financial :: Accounting
        """.strip().splitlines(),
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'tappio-extract = tappio.scripts.extract:main',
            'tappio-graph = tappio.scripts.graph:main',
            'tappio-indent = tappio.scripts.indent:main',
            'tappio-merge = tappio.scripts.merge:main',
            'tappio-missing-accounts = tappio.scripts.missing_accounts:main',
            'tappio-move-entries = tappio.scripts.move_entries:main',
            'tappio-print-accounts = tappio.scripts.print_accounts:main',
            'tappio-print-earnings = tappio.scripts.print_earnings:main',
            'tappio-renumber = tappio.scripts.renumber:main',
        ]
    },
)
