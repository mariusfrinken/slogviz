#!/usr/bin/env python3
import glob
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
parser.add_argument("-m", "--multiple_at_once", type=int, default=0, help="0 if one plot per file, 1 if one plot containing all files, 2 if one timeline plot with all files")
parser.add_argument("-j", "--export_to_JSON", type=int, default=0, help="if set to 1, one JSON file per logfile will be created")
parser.add_argument("-s", "--select_by_sources",default='', help="a string containing the name sources, trailed by a ','")
#parser.add_argument("-i", "--ignore_source",default='', help="a string containing the name of a source only")
parser.add_argument("-w", "--web_view", type=int, default=0, help="if set to 1, an interactive website will be hosted on the localhost")

args = parser.parse_args()
if args.select_by_sources == 'all' or args.select_by_sources == '': #input sanitazation
	pass
files = glob.glob("./resources/*"+args.filename_pattern+"*")
logfiles = [readin(x) for x in files]
if args.export_to_JSON:
	for x in logfiles:
		x.export_to_JSON()
elif logfiles:
	# for l in logfiles:
	# 	plot_single_file_multiple_sources(l,l.sources)
	# 	show()
	# 	print(l.sources)
	if args.web_view==0:
		superplot(logfiles,args.remove_redundant_entries,args.select_by_sources)
		#correlate_multiple_files(logfiles,[mock_rule_mult])
		#correlate_single_file(logfiles[0],[mock_rule])
	elif args.web_view==1:
		webview_run(logfiles)