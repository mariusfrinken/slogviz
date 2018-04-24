# -*- coding: utf-8 -*-
"""The main routine of SLogVIZ.
It loads all files given by the file_names command line argument and prompts the user to decide for further analysis steps.


In this file, the Command Line Arguments of SLogVIZ are defined:
	required:
		-f -- a string containing the names of files to visualize, trailed by a ','
			example: -f syslog,auth.log
	optional:
		-j -- an integer, if set to 1, one JSON file per logfile will be created, if set to 2 the structured_data field will be left empty in order to save place
			example: -j 1
		-t -- a string representing an offset that shall be added to all timestamps without timezone information (default '+0000'),
			'+0100' equals UTC plus one hour
			example: -t +0100
		-r -- a binary digit, when set to 1, all entries from the same logfile with the same timestamp will be removed,
			except for one, in most plots
			example: -r 1
		-s -- a string that should contain sources, trailed by a ',', used for filtering out all entries that have sources which are NOT in the select_string
			example: -s sudo,sshd,su

Exported functions:
main -- the main loop of SLogVIZ
"""

import re
import time
import importlib
import argparse
import platform
from inspect import getmembers, isfunction

from .logfileclasses import *
from .logfileparser import *
from .plotter import *

# START internal functions
def _transform_select_string(select_string, logfiles):
	"""This function takes a string and a list of logfiles and returns a list of strings.

	Positional Arguments:
	selected_string -- a string that should contain sources, trailed by a ','
	logfiles -- a list logfile objects

	Returns:
	a list of strings, representing  the intersection of all sources that are found in the selected_string
	and in the elements of the logfiles list.
	"""
	selected_sources = []
	for log in logfiles:
		tmp = select_string.split(',')
		for s in tmp:
			if s in log.sources and s not in selected_sources:
				selected_sources.append(s)
	if len(selected_sources) == 0:
		for log in logfiles:
			selected_sources += [x for x in log.sources if x not in selected_sources]
	return selected_sources

def _print_action_list(list, exit=True):
	"""Prints a list of possible actions and their related indices.

	Positional Arguments:
	list -- a list of strings, possible actions of the user

	Keyword Arguments:
	exit -- boolean, whether the option to exit/return shall be printed (default True)
	"""
	print("Please enter the index of one of the following options:")
	for x in list:
		print("{}:	{}".format(list.index(x),x))
	if exit:
		print("{}:	{}".format(len(list),"exit/return"))
	print("===================================================")

def _print_welcome():
	"""Print the welcome message and sleep for one second."""
	print("####################################################")
	print("# Welcome to SLogVIZ, a simple Log file Visualizer #")
	print("####################################################")
	print()
	time.sleep(1)

def _print_bye():
	"""Print the goodbye message, sleep for one second and delete the goodbye message."""
	print("####################################################")
	print("#                       Bye                        #")
	print("####################################################")
	time.sleep(1)
	_delete_print(4)

def _delete_print(number):
	"""Deletes a number of lines from stdout.
	Used to reduce redundant or temporal data from the command line interface.

	Keyword arguments:
	number -- the amount of lines to delete (default 1)
	"""
	if not platform.system() == "Windows":#Windows does not fully implement ANSI Control Characters, see README
		print('\x1b[1A\x1b[2K'*number)

def _edit_selected_sources(original_selected_sources, available_sources):
	"""This function provides the user a possibility to interactively change the select_by_sources argument.

	Positional Arguments:
	original_selected_sources -- a list of strings, representing the sources currently stored in the select_by_sources argument
	available_sources -- all source of all loaded logfile objects, that are not in original_selected_sources

	Returns:
	a string that should contain sources, trailed by a ',',
	"""
	ret = original_selected_sources
	while(True):
		list_of_actions = ["remove sources from selection", "add sources to selection", "reset the filter", "empty selection"]
		_print_action_list(list_of_actions)
		line = input("$ ")
		_delete_print(len(list_of_actions)+5)
		if line == "0":
			while(True):
				_print_action_list(ret)
				line = input("$ ")
				_delete_print(len(ret)+5)
				if line.isdigit():
					line = int(line)
					if line == len(ret):
						break
					elif line in [ret.index(x) for x in ret]:
						available_sources.append(ret[line])
						del ret[line]
		elif line == "1":
			while(True):
				_print_action_list(available_sources)
				line = input("$ ")
				_delete_print(len(available_sources)+5)
				if line.isdigit():
					line = int(line)
					if line == len(available_sources):
						break
					elif line in [available_sources.index(x) for x in available_sources]:
						ret.append(available_sources[line])
						del available_sources[line]
		elif line == "2":
			ret = original_selected_sources
		elif line == "3":
			available_sources += ret
			ret = []
		elif line == "4":
			return ",".join(ret)

def _change_remove_redundant():
	"""This function provides the user a possibility to interactively change the remove_redundant_entries argument.

	Returns:
	an integer, the new chosen value for remove_redundant_entries
	"""
	list_of_actions = ["keep entries with the exact same timestamp", "remove such entries, less visual clutter"]
	ret = 0
	while True:
		_print_action_list(list_of_actions)
		line = input("$ ")
		_delete_print(len(list_of_actions)+5)
		if line == "0":
			ret = 0
			break
		elif line == "1":
			ret = 1
			break
		elif line == "2":
			break
	return ret

def _correlate(logfiles):
	"""This function implements an interactive menu where the user may correlate logfile object with
	correlation rules present in a file called 'rules.py', that must be present in the current working directory.

	Positional Arguments:
	logfiles -- a list of logfile objecs, which shall be correlated
	"""
	try:
		module = importlib.import_module("rules")
	except ImportError:
		print("rules.py needs to be present in this directory")
		time.sleep(2)
		_delete_print(2)
		return
	else:
		list_of_actions = [x for x,y in getmembers(module, isfunction) if not x.startswith('_')]
		list_of_entries = []
		for log in logfiles:
			list_of_entries += log.content
		while True:
			_print_action_list(list_of_actions)
			line = input("$ ")
			_delete_print(len(list_of_actions)+5)
			if line.isdigit():
				line = int(line)
				if line == len(list_of_actions):
					break
				elif line in [list_of_actions.index(x) for x in list_of_actions]:
					func = getattr(module, list_of_actions[line])
					ret = func(list_of_entries)
					if len(ret) == 0:
						pass
					else:
						new_list = ["plot result", "print result to result.txt file"]
						while True:
							_print_action_list(new_list, exit=False)
							new_line = input("$ ")
							_delete_print(len(new_list)+4)
							if new_line == "0":
								plot_correlated(ret, logfiles, list_of_actions[line])
								show()
								break
							elif new_line == "1":
								fp = open('result.txt','w')
								names = ' and '.join([l.name for l in logfiles])
								print("Result of {} evaluated against all entries from {}:".format(list_of_actions[line], names), file=fp)
								for x in ret:
									print(x, file=fp)
								fp.close()
								print("result.txt was written")
								time.sleep(1)
								_delete_print(2)
								break
# END of internal functions

#START exported functions
def main():
	"""The interactive main loop of SLogVIZ."""
	parser = argparse.ArgumentParser(prog='slogviz')
	parser.add_argument("-f", "--file_names", required=True, help="a string containing the names of files to visualize, trailed by a ','")
	parser.add_argument("-r", "--remove_redundant_entries", type=int, default=0, help="a binary digit, when set to 1, all entries from the same logfile with the same timestamp will be removed, except for one, in most plots")
	parser.add_argument("-j", "--export_to_JSON", type=int, default=0, help="if set to 1, one JSON file per logfile will be created, if set to 2 the structured_data field will be left empty in order to save place")
	parser.add_argument("-s", "--select_by_sources",default='', help="a string containing the name sources, trailed by a ',' used for filtering out all entries that have sources which are NOT in the select_string")
	parser.add_argument("-t", "--time_offset", default='', help="a string containing the time offset from UTC, may be used if syslog files are saved without timezone information")
	args = parser.parse_args()

	_print_welcome()
	file_names = args.file_names.split(',')
	p = re.compile(r'^[+-]{1}(\d){4}$')
	m = p.match(args.time_offset)
	if m:
		logfiles = [readin(x, time_offset=args.time_offset) for x in file_names]
	else:
		logfiles = [readin(x) for x in file_names]
	logfiles = [x for x in logfiles if x ]
	_delete_print(4)

	#when one or more files could not be parsed
	if not len(logfiles) == len(file_names):
		for x in file_names:
			if x not in [y.name for y in logfiles]:
				print("file " + x + " can not be parsed!")
				time.sleep(2)
				_delete_print(2)

	#when all files could not be parsed
	if len(logfiles) == 0:
		print("No file was given with the -f argument that slogviz can parse")
		print()
		_print_bye()
		return

	if args.export_to_JSON:
		for x in logfiles:
			x.export_to_JSON(sparse=(args.export_to_JSON == 2))
	else:
		list_of_actions = ["plot single timeline(s)", "plot single timeline(s), colorcoded by source", "plot single timeline bar chart(s)", "plot multiple timeline", "plot overview timeline", "produce all plots", "filter by sources (does not affect option 2 and 4)", "filter redundant timestamps (does not affect option 2 and 4)", "correlate with rules.py"]
		while True:
			_print_action_list(list_of_actions)
			line = input("$ ")
			if line == "0":
				for log in logfiles:
					plot_single(log,args.remove_redundant_entries, args.select_by_sources)
					show()
				_delete_print(len(list_of_actions)+5)
			elif line == "1":
				_delete_print(len(list_of_actions)+5)
				new_list = ["frequent sources in the background","frequent sources in the foreground"]
				while True:
					_print_action_list(new_list, exit=False)
					line = input("$ ")
					if line == "0":
						background = True
						break
					elif line == "1":
						background = False
						break
					else:
						_delete_print(len(new_list)+4)
				for log in logfiles:
					plot_single_file_colored(log, args.remove_redundant_entries, args.select_by_sources, rev=background)
					show()
				_delete_print(len(new_list)+4)
			elif line == "2":
				frame_seconds = None
				print("please define a frame in seconds")
				while True:
					frame_seconds = input("$ ")
					if frame_seconds.isdigit():
						frame_seconds = int(frame_seconds)
						break
					else:
						_delete_print(2)
				_delete_print(3)
				for log in logfiles:
					plot_bar_chart(log, frame_seconds=frame_seconds)
					show()
				_delete_print(len(list_of_actions)+5)
			elif line == "3":
				plot_multiple_timeline(logfiles,args.remove_redundant_entries,args.select_by_sources)
				show()
				_delete_print(len(list_of_actions)+5)
			elif line == "4":
				plot_timeline_overview(logfiles)
				show()
				_delete_print(len(list_of_actions)+5)
			elif line == "5":
				superplot(logfiles,args.remove_redundant_entries, args.select_by_sources)
				show()
				_delete_print(len(list_of_actions)+5)
			elif line == "6":
				_delete_print(len(list_of_actions)+5)
				selected_sources = _transform_select_string(args.select_by_sources, logfiles)
				available_sources = []
				for log in logfiles:
					available_sources += [x for x in log.sources if x not in selected_sources]
				args.select_by_sources = _edit_selected_sources(selected_sources,available_sources)
			elif line == "7":
				_delete_print(len(list_of_actions)+5)
				args.remove_redundant_entries = _change_remove_redundant()
			elif line == "8":
				_delete_print(len(list_of_actions)+5)
				_correlate(logfiles)
			elif line == "9":
				_delete_print(len(list_of_actions)+5)
				break
			else:
				_delete_print(len(list_of_actions)+5)
		_print_bye()
#END exported functions

