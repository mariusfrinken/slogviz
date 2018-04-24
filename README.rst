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

1. install Python 3.6 or higher (PIP shall be installed and the PATH variable needs to include Python, these things should be handled by the default installation process)
2. download the latest version of SLogVIZ here_ and extract the .zip file
3. decide whether to install the program or to NOT install it

install:

4. navigate to the slogviz root directory and enter

   * UNIX: ``python3 setup.py install`` in a terminal
   * WINDOWS: ``.\setup.py install`` in the cmd.exe or Windows-Powershell
5. now the program can be executed by entering ``python3 -m slogviz`` or ``python -m slogviz`` in any working directory

local usage:

4. open a console and navigate to the slogviz root directory and enter ``pip install -r requirements.txt`` (or ``pip3 install -r requirements.txt``)
5. now the program can be executed by entering ``python -m slogviz``, but only in the slogviz root directory

When executing the module with one or more log files passed via the ``-f`` argument, the main loop will be displayed:

.. image:: https://raw.githubusercontent.com/mariusfrinken/slogviz/assets/menu.png

When selecting a plot, a new Window will be opened with the chosen visualization. After closing this window, the main loop is presented again.

Inside the ``testfiles`` directory are some sample log files, which might help to understand the usage of SLogVIZ.

Plots
######

All plots produced by SLogVIZ are generated with the **matplotlib** module, thus the plot window offers various options to interact with it. Additionally, SLogVIZ has a neat feature, that in most plots one can hover with the mouse over a data point and get information about the related log file entry in a text box.

For a detailed description of the different plots offered by SLogVIZ, please see the wiki_.

Advanced Usage
################

Filtering
~~~~~~~~~

For filtering log files before visualizing, use the command line options or their interactive counterparts, option 6 & 7 in the main loop.

Generally a look at the ouput of ``python3 -m slogviz -h`` maybe helpful in order to see what command line arguments are used by SLogVIZ .

Correlation
~~~~~~~~~~~~

SLogVIZ is also able to evaluate log file entries against correlation rules written in Python.

For this purpose, a correlation rule needs to be defined as a function in a file named ``rules.py`` inside the current working directory. SLogVIZ comes with a sample file of this type, please refer to its documentation for further instructions on how to write correlation rules.

Once such a file is present, simply execute SLogVIZ with the files you want to correlate and choose option 8 in the main loop.


License and other legal stuff
-------------------------------
This tool is published under the MIT License, see `LICENCE
<https://github.com/mariusfrinken/slogviz/blob/master/LICENSE>`_.

The author wants to clarify that SLogVIZ is not meant to serve as a total replacement of conventional log analysis tools and methods.

Contributing to SLogVIZ
-------------------------
Please refer to the wiki_.


.. _wiki: https://github.com/mariusfrinken/slogviz/wiki
.. _here: https://github.com/mariusfrinken/slogviz/archive/master.zip





