# -*- coding: utf-8 -*-

import re
import argparse
import collections


from .logfileclasses import *
from .plotter import *
from .logfileparser import *
from .webview import *
from .correlator import *

# START of functions
def transform_select_string(select_string, logfiles):
	selected_sources = []
	for log in logfiles:
		tmp = select_string.split(',')
		for s in tmp:
			if s in log.sources:
				selected_sources.append(s)
			elif s:
				pass
				#print("{} does not contain an entry from the source: '{}'".format(logfile.name,s))
		if len(selected_sources) == 0:
			selected_sources += log.sources
	return selected_sources

def print_action_list(list):
	print("Please enter the index of one of the following options:")
	for x in list:
		print("{}:		{}".format(list.index(x),x))
	print("{}:		{}".format(len(list),"exit/return"))
	print("===================================================")

def print_welcome():
	print("####################################################")
	print("# Welcome to SLogVIZ, a simple Log file Visualizer #")
	print("####################################################")
	print()

def edit_selected_sources(original_selected_sources, available_sources):
	ret = original_selected_sources
	print("===================================================")
	print("Editing the selected sources")
	while(True):
		list_of_actions = ["remove sources", "add sources", "reset the list"]
		print_action_list(list_of_actions)

		line = input("$ ")
		if line == "0":
			while(True):
				print_action_list(ret)
				line = input("$ ")
				print()
				if line.isdigit():
					line = int(line)
					if line == len(ret):
						break
					elif line in [ret.index(x) for x in ret]:
						available_sources.append(ret[line])
						del ret[line]
		elif line == "1":
			while(True):
				print_action_list(available_sources)
				line = input("$ ")
				print()
				if line.isdigit():
					line = int(line)
					if line == len(available_sources):
						break
					elif line in [available_sources.index(x) for x in available_sources]:
						ret.append(available_sources[line])
						del available_sources[line]
		elif line == "2":
			ret = original_selected_sources
			print("resetted the selected sources")
		elif line == "3":
			return ",".join(ret)

	return ret


# END of functions

#START of main programm
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename_pattern", help="only files containing this pattern will be opened", default="log")
parser.add_argument("-r", "--remove_redundant_entries", type=int, default=0, help="0 if entries with the same date should stay, 1 if they shall be removed in the graphical output")
parser.add_argument("-j", "--export_to_JSON", type=int, default=0, help="if set to 1, one JSON file per logfile will be created")
parser.add_argument("-s", "--select_by_sources",default='', help="a string containing the name sources, trailed by a ','")
parser.add_argument("-w", "--web_view", type=int, default=0, help="if set to 1, an interactive website will be hosted on the localhost")

def main():
	#print("got ya")
	args = parser.parse_args()
	file_names = args.filename_pattern.split(',')

	#files = glob.glob(file_names)
	logfiles = [readin(x) for x in file_names]
	logfiles = [x for x in logfiles if x ]

	if args.web_view:
		webview_run(logfiles)
	elif args.export_to_JSON:
		for x in logfiles:
			x.export_to_JSON()
	else:
		print_welcome()
		list_of_actions = ["plot single timeline", "plot multiple timeline", "plot overview timeline", "produce all plots", "edit filter"]

		while True:
			print_action_list(list_of_actions)
			line = input("$ ")
			print()
			if line == "0":
				for log in logfiles:
					plot_single(log,args.remove_redundant_entries, args.select_by_sources)
					show()
			elif line == "1":
				plot_multiple(logfiles,args.remove_redundant_entries,args.select_by_sources)
				show()
			elif line == "2":
				plot_multiple_timeline(logfiles,args.remove_redundant_entries,args.select_by_sources)
				show()
			elif line == "3":
				superplot(logfiles,args.remove_redundant_entries, args.select_by_sources)
				show()
			elif line == "4":
				selected_sources = transform_select_string(args.select_by_sources, logfiles)
				available_sources = []
				for log in logfiles:
					available_sources += [x for x in log.sources if x not in selected_sources]
				args.select_by_sources = edit_selected_sources(selected_sources,available_sources)
			elif line == "5":
				break

		print("####################################################")
		print("#                       Bye                        #")
		print("####################################################")

	# elif logfiles:
	# 	# for l in logfiles:
	# 	# 	plot_single_file_multiple_sources(l,l.sources)
	# 	# 	show()
	# 	# 	print(l.sources)
	# 	if args.web_view==0:
	# 		superplot(logfiles,args.remove_redundant_entries,args.select_by_sources)
	# 		#correlate_multiple_files(logfiles,[mock_rule_mult])
	# 		#correlate_single_file(logfiles[0],[mock_rule])
	# 		pass

