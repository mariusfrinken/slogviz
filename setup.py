#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from setuptools import find_packages, setup

with open('LICENSE') as f:
	LICENSE = f.read()

with open('requirements.txt') as f:
	REQUIRED = f.readlines()

# Package meta-data.
NAME = 'slogviz'
DESCRIPTION = 'SLogVIZ is an Simple Log file Visualizer written in Python. It visualizes log files and correlations found among log file entries using matplotlib.'
URL = 'https://github.com/mariusfrinken/slogviz'
EMAIL = 'marius.frinken@fau.de'
AUTHOR = 'Marius Frinken'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = ''


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
	exec(f.read(), about)

setup(
	name=NAME,
	version=about['__version__'],
	description=DESCRIPTION,
	long_description=long_description,
	author=AUTHOR,
	author_email=EMAIL,
	python_requires=REQUIRES_PYTHON,
	url=URL,
	packages=find_packages(exclude=('tests','docs')),
	install_requires=REQUIRED,
	include_package_data=True,
	license=LICENSE,
	classifiers=[
		# Trove classifiers
		# Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Topic :: Internet :: Log Analysis',
		'Topic :: System :: Logging',
		'Operating System :: OS Independent'
	],
)