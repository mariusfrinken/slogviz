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

File Formats
#########################
At the current state, SLogVIZ is able to parse syslog file , Windows Event Log (evtx) files and SQLite files created by Firefox and Chrome. Due to different timestamps definitions, SLogVIZ may not be able to read all entries of evtx files, when using Windows. In this case a warning is sent to the user.

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
You have the choice, the module can be used with or without installing it.

General steps:

1. install Python 3.6 or higher
2. download slogviz
3. decide whether to install the program or to NOT install it

install:

4. open a console and navigate to the slogviz root directory and enter UNIX: ``python setup.py install`` in a terminal or WINDOWS: ``.\setup.py install`` in the cmd.exe or Windows-Powershell
5. now the program can be executed by entering ``python -m slogviz``

local usage:

4. open a console and navigate to the slogviz root directory and enter ``pip install -r requirements.txt``
5. now the program can be executed by entering ``python -m slogviz``, but only in the slogviz root directory

Windows 10:

On how to enable ANSI Terminal Control: `See this superuser answer
<https://superuser.com/a/1300251>`_.


Contributing to SLogVIZ
-------------------------
This is my first Python and github project, so please contact me if you have any questions or suggestions:
``marius.frinken<at>fau.de``

<some information for developers interested in contributing to this project>

Style
#########################
In this project, I used *tabs* for indentation. As one of my professor likes to say "I don't believe in numbers greater than 3", I personally find it irritating to see multiple spaces instead of one tab symbol in my code.









