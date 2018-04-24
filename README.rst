=========================
SLogVIZ
=========================
**SLogVIZ** is an **Simple Log file Visualizer** written in Python.
It visualizes log files and correlations found among log file entries using `matplotlib
<https://matplotlib.org/>`_.

**This project is currently under construction!**

.. image:: https://raw.githubusercontent.com/mariusfrinken/slogviz/assets/screenshot.png

Introduction
-------------------------
SLogVIZ is designed to be a helpful tool for forensic investigations, by producing visualizations of log files.

File Formats
#########################
At the current state, SLogVIZ is able to parse syslog files , Windows Event Log (evtx) files and SQLite files created by Firefox and Chrome. Due to different timestamps definitions, SLogVIZ may not be able to read all entries of evtx files, when using Windows. In this case a warning is sent to the user.

In order to parse any file, the filename and extension needs to be as follows:

==================  ====================================  ==============================
 File Formats        File Names/Extensions                 Examples
==================  ====================================  ==============================
 syslog              \*log                                 syslog, auth.log, system.log
 evtx                \*.evtx                               System.evtx
 SQLite - Firefox    \*places.sqlite                       places.sqlite, case42_places.sqlite
 SQLite - Chrome     \*History                             History, case42_History
 JSON                \*.slogviz.json                       syslog.slogviz.json
==================  ====================================  ==============================

Installing and Using
-------------------------
SLogVIZ is intended to be executed as a Python module with the Python3 interpreter. Therefore, users have the choice to either install SLogVIZ or just install all dependencies and use SLogVIZ without installing it.

Here is a simple guide on how to get SLogVIZ working:

1. install Python 3.6 or higher
2. download the latest version of SLogVIZ here_ and extract the .zip file
3. decide whether to install the program or to NOT install it

install:

4. navigate to the slogviz root directory and enter
	a. UNIX: ``python3 setup.py install`` in a terminal
	b. WINDOWS: ``.\setup.py install`` in the cmd.exe or Windows-Powershell
5. now the program can be executed by entering ``python3 -m slogviz`` or ``python -m slogviz`` in any working directory

local usage:

4. open a console and navigate to the slogviz root directory and enter ``pip install -r requirements.txt``
5. now the program can be executed by entering ``python -m slogviz``, but only in the slogviz root directory

Windows 10:

On how to enable ANSI Terminal Control: `See this superuser answer
<https://superuser.com/a/1300251>`_.


.. image:: https://raw.githubusercontent.com/mariusfrinken/slogviz/assets/menu.png

License and other legal stuff
-------------------------------
This tool is published under the MIT License, see `LICENCE
<https://raw.githubusercontent.com/mariusfrinken/slogviz/master/LICENSE>`_.

The author wants to clarify that SLogVIZ is not meant to serve as a total replacement of conventional log analysis tools and methods.

Contributing to SLogVIZ
-------------------------
Please refer to the `Wiki
<https://github.com/mariusfrinken/slogviz/wiki>`_.

.. _here: https://github.com/mariusfrinken/slogviz/archive/master.zip





