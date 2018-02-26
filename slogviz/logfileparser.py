import re
import datetime
import json
from logfileclasses import *

"""Reads in a file and stores the content.
Returns a logfile Object containg all this data.
"""
def readin(file):
	p = re.compile(r'^.*log$')
	if p.match(file):
		return readin_syslog(file)
	else:
		p2 = re.compile(r'^.*json$')
		if p2.match(file):
			return readin_JSON(file)
		else:
			print('file format not supported')
			return None


"""Reads in a file of the syslog format."""
def readin_syslog(file):
	f = open(file, 'r')
	counter = 0
	content = []
	sources = []
	p = re.compile(r'^(\D{3,3}\s+\d+\s\d{2,2}:\d{2,2}:\d{2,2})\s(\S+)\s([^\][:]+)(\[\d+\]){0,1}:\s(.*)$')
	for x in f.readlines():
		counter+=1
		m = p.search(x)
		formatted_date = datetime.datetime.strptime("2017 " + m.group(1),"%Y %b %d %H:%M:%S")
		#formatted_date = datetime.datetime.strptime(m.group(1),"%b %d %H:%M:%S")
		content.append(logfile_entry(counter,m.group(5),m.group(0),formatted_date,m.group(2),m.group(3)))
		if not m.group(3) in sources:
			sources.append(m.group(3))
	f.close()
	lf = logfile(file, counter, 'syslog', content,sources)
	return lf


"""Reads in a JSON file"""
def readin_JSON(file):

	def object_decoder(obj):
		"""This function is used to properly load the JSON elements into the corresponding classes."""
		if 'logfile' in obj:
			return logfile(obj['logfile']['name'], obj['logfile']['lines'], obj['logfile']['type'], obj['logfile']['content'], obj['logfile']['sources'])
		if 'logfile_entry' in obj:
			date = datetime.datetime.strptime(obj['logfile_entry']['date']['datetime'],"%Y-%m-%dT%H:%M:%S")
			return logfile_entry(obj['logfile_entry']['line_nr'],obj['logfile_entry']['message'], obj['logfile_entry']['full_line'], date,obj['logfile_entry']['hostname'],obj['logfile_entry']['source'])
		return obj

	fp = open(file,'r')
	lf = json.load(fp, object_hook=object_decoder)
	fp.close()
	return lf
