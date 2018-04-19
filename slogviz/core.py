# -*- coding: utf-8 -*-
"""The main routine of SLogVIZ.
It loads all files given by the file_names command line argument and prompts the user to decide for further analysis steps.


Command line arguments:

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

# START of  internal functions
def _transform_select_string(select_string, logfiles):
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

def _print_action_list(list):
	print("Please enter the index of one of the following options:")
	for x in list:
		print("{}:	{}".format(list.index(x),x))
	print("{}:	{}".format(len(list),"exit/return"))
	print("===================================================")

def _print_welcome():
	print("####################################################")
	print("# Welcome to SLogVIZ, a simple Log file Visualizer #")
	print("####################################################")
	print()
	time.sleep(1)

def _print_bye():
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
	ret = original_selected_sources
	while(True):
		list_of_actions = ["remove sources from selection", "add sources to selection", "reset the filter"]
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
			return ",".join(ret)
	return ret

def _change_remove_redundant():
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
						plot_correlated(ret, logfiles, list_of_actions[line])
						show()



# END of internal functions

#START of main program
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file_names", required=True, help="a string containing the names of files to visualize, trailed by a ','", default="")
parser.add_argument("-r", "--remove_redundant_entries", type=int, default=0, help="0 if entries with the same date should stay, 1 if they shall be removed in the graphical output")
parser.add_argument("-j", "--export_to_JSON", type=int, default=0, help="if set to 1, one JSON file per logfile will be created, if set to 2 the structured_data field will be left empty in order to save place")
parser.add_argument("-s", "--select_by_sources",default='', help="a string containing the name sources, trailed by a ','")

def main():
	args = parser.parse_args()

	_print_welcome()
	file_names = args.file_names.split(',')
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
		list_of_actions = ["plot single timeline(s)", "plot single timeline(s), colorcoded by source", "plot single timeline bar chart(s)", "plot multiple timeline", "plot overview timeline", "produce all plots", "filter by sources (does not affect option 2 or 4)", "edit remove_redundant_entries", "correlate with rules.py"]
		while True:
			_print_action_list(list_of_actions)
			line = input("$ ")
			if line == "0":
				for log in logfiles:
					plot_single(log,args.remove_redundant_entries, args.select_by_sources)
					show()
				_delete_print(len(list_of_actions)+5)
			elif line == "1":
				for log in logfiles:
					plot_single_file_multiple_sources(log, args.remove_redundant_entries, args.select_by_sources)
					show()
				_delete_print(len(list_of_actions)+5)
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
					scatter_plot(log, frame_seconds=frame_seconds)
					show()
				_delete_print(len(list_of_actions)+5)
			elif line == "3":
				plot_multiple(logfiles,args.remove_redundant_entries,args.select_by_sources)
				show()
				_delete_print(len(list_of_actions)+5)
			elif line == "4":
				plot_multiple_timeline(logfiles)
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


