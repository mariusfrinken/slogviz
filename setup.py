#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from setuptools import find_packages, setup, Command

with open('LICENSE') as f:
	LICENSE = f.read()

with open('requirements.txt') as f:
	REQUIRED = f.readlines()

# Package meta-data.
NAME = 'slogviz'
DESCRIPTION = 'My short description for my project.'
URL = 'https://github.com/me/myproject'
EMAIL = 'marius.frinken@fau.de'
AUTHOR = 'Marius Frinken'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = ''


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = '\n' + f.read()

about = {}
if not VERSION:
	with open(os.path.join(here, NAME, '__version__.py')) as f:
		exec(f.read(), about)
else:
	about['__version__'] = VERSION


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
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy'
	],
)