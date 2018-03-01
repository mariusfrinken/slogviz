#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import glob
import re
import argparse


from logfileclasses import *
from plotter import *
from logfileparser import *
from webview import *
from correlator import *


#START of functions



#END of functions

#START of main programm
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename_pattern", help="only files containing this pattern will be opened", default="log")
parser.add_argument("-r", "--remove_redundant_entries", type=int, default=0, help="0 if entries with the same date should stay, 1 if they shall be removed in the graphical output")
parser.add_argument("-j", "--export_to_JSON", type=int, default=0, help="if set to 1, one JSON file per logfile will be created")
parser.add_argument("-s", "--select_by_sources",default='', help="a string containing the name sources, trailed by a ','")
parser.add_argument("-w", "--web_view", type=int, default=0, help="if set to 1, an interactive website will be hosted on the localhost")

args = parser.parse_args()
file_names = args.filename_pattern.split(',')

#files = glob.glob(file_names)
logfiles = [readin(x) for x in file_names]
logfiles = [x for x in logfiles if x ]
list_of_plots = ["st","mt","all"]
print("Welcome to the CLI of SLogVIZ, a simple Log file Visualizer.")
print("Please enter one of the following options:")
for x in list_of_plots:
	print(x)
print("==========================================")
while True:
	line = input()
	if line == "st":
		for log in logfiles:
			plot_single(log,args.remove_redundant_entries, args.select_by_sources)
			show()
	elif line == "abort":
		break
	elif line == "all":
		superplot(logfiles,args.remove_redundant_entries, args.select_by_sources)
	elif line == "mt":
		plot_multiple(logfiles,args.remove_redundant_entries,args.select_by_sources)


# if args.export_to_JSON:
# 	for x in logfiles:
# 		x.export_to_JSON()
# elif logfiles:
# 	# for l in logfiles:
# 	# 	plot_single_file_multiple_sources(l,l.sources)
# 	# 	show()
# 	# 	print(l.sources)
# 	if args.web_view==0:
# 		superplot(logfiles,args.remove_redundant_entries,args.select_by_sources)
# 		#correlate_multiple_files(logfiles,[mock_rule_mult])
# 		#correlate_single_file(logfiles[0],[mock_rule])
# 	elif args.web_view==1:
# 		webview_run(logfiles)