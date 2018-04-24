# -*- coding: utf-8 -*-

"""The sub module of slogviz, that parses log files and returns logfileclasses.logfile objects.

Exported functions:
readin(file) -- Reads in a file and returns a logfileclasses.logfile object.
"""

import platform
import re
import datetime
import time
import json
import sqlite3 as lite
import Evtx.Evtx as evtx
import untangle

from .logfileclasses import *

#START internal functions
def _print_progress(counter):
	"""Prints one line with the number of the parsed entry.
	The line is ended by a carriage return.

	Positional arguments:
	counter -- the number to print
	"""
	print('parse log file entry nr: {}'.format(counter),end='\r')

def _delete_print(number=1):
	"""Deletes a number of lines from stdout.
	Used to reduce redundant or temporal data from the command line interface.

	Keyword arguments:
	number -- the amount of lines to delete (default 1)
	"""
	if not platform.system() == 'Windows':#Windows does not fully implement ANSI Control Characters, see README
		print('\x1b[2K\x1b[1A'*number)

def _readin_syslog(file, time_offset='+0000'):
	"""Reads in a file of the syslog format.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to be read in as a string, here name euqals path to the file

	Keyword arguments:
	time_offset -- a offset that shall be added to all timestamps without timezone information (default '+0000')
					'+0100' equals UTC plus one hour
	"""
	f = open(file, 'r')
	counter = 0
	content = []
	sources = []
	p = re.compile(r'^(\D{3}\s+\d+\s\d{2}:\d{2}:\d{2})\s(\S+)\s([^\][:]+)(\[\d+\]){0,1}([^:])*:\s(.*)$')
	p2 = re.compile(r'^.*---\slast\smessage\srepeated\s\d+\stime[s]{0,1}\s---$')
	precise_date = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2})\s(\S+)\s([^\][:]+)(\[\d+\]){0,1}([^:])*:\s(.*)$')

	for x in f.readlines():
		counter+=1
		m = p.search(x)
		_print_progress(counter)
		if m:
			# default syslog line was read, herre we assign the year 2017 to all timestamps
			formatted_date = datetime.datetime.strptime('2017 ' + m.group(1)+ time_offset,"%Y %b %d %H:%M:%S%z")
			content.append(logfile_entry(counter, file, m.group(6), m.group(0), formatted_date, m.group(2),m.group(3)))
			if not m.group(3) in sources:
				sources.append(m.group(3))
		elif p2.search(x):
			# a message syaing "last message repeated x times" was read, here we simply ignore such lines
			counter -= 1
		else:
			m3 = precise_date.search(x)
			if m3:
				# precise timestamps are detected
				unformatted_date = m3.group(1)
				unformatted_date = unformatted_date[:-3]+unformatted_date[-2:]
				# this hack around is not needed in Python 3.7, see https://bugs.python.org/issue15873
				formatted_date = datetime.datetime.strptime(unformatted_date,"%Y-%m-%dT%H:%M:%S.%f%z")
				content.append(logfile_entry(counter, file, m3.group(6), m3.group(0), formatted_date, m3.group(2), m3.group(3)))
				if not m3.group(3) in sources:
					sources.append(m3.group(3))
			else:
				# in case no prior regex matches, the line is added to the line read before
				if len(content) > 0:
					content[-1].message += x
					content[-1].structured_data += x
					counter -= 1
				else:
					counter -= 1
					pass
	f.close()
	_delete_print()
	lf = logfile(file, counter, 'syslog', content,sources)
	return lf

def _readin_JSON(file):
	"""Reads in a file of the JSON format created by a previous slogviz process.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	def object_decoder(obj):
		"""This function is used to properly load the JSON elements into the corresponding classes."""
		if 'logfile' in obj:
			return logfile(obj['logfile']['name'], obj['logfile']['lines'], obj['logfile']['type'], obj['logfile']['content'], obj['logfile']['sources'])
		if 'logfile_entry' in obj:
			if len(obj['logfile_entry']['timestamp']['datetime']) >= 20 :
				date = datetime.datetime.strptime(obj['logfile_entry']['timestamp']['datetime'],"%Y-%m-%dT%H:%M:%S.%f")
			elif obj['logfile_entry']['timestamp']['datetime'][-6:-5] != '+':
				date = datetime.datetime.strptime(obj['logfile_entry']['timestamp']['datetime'],"%Y-%m-%dT%H:%M:%S")
			else:
				unformatted_date = obj['logfile_entry']['timestamp']['datetime']
				unformatted_date = unformatted_date[:-3]+unformatted_date[-2:]
				# once again, related to missing features in Python 3.6
				date = datetime.datetime.strptime(unformatted_date,"%Y-%m-%dT%H:%M:%S.%f%z")
			return logfile_entry(obj['logfile_entry']['id'], file, obj['logfile_entry']['message'], obj['logfile_entry']['structured_data'], date,obj['logfile_entry']['hostname'],obj['logfile_entry']['source'])
		return obj

	fp = open(file,'r')
	lf = json.load(fp, object_hook=object_decoder)
	fp.close()
	return lf

def _readin_chrome_history(file):
	"""Reads in a file of the SQLite format created by Google Chrome.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	con = lite.connect(file)
	content = []
	with con:
		cur = con.cursor()
		cur.execute("SELECT visits.id, urls.url, datetime(visits.visit_time / 1000000 + (strftime('%s', '1601-01-01')), 'unixepoch'), * FROM urls, visits WHERE urls.id = visits.url;")
		rows = cur.fetchall()
		sources = []
		for row in rows:
			_print_progress(rows.index(row))
			date = datetime.datetime.strptime(row[2],"%Y-%m-%d %H:%M:%S")
			source = ''
			pattern = re.compile(r'.*(www\.|http[s]{0,1}:\/\/)([^\.]+)\..*')
			m = pattern.match(row[1])
			if m:
				source = m.group(2)
				if not source in sources:
					sources.append(source)
			content.append(logfile_entry(row[0], file, row[1], row[3:], date, '', source))
	_delete_print()
	return logfile(file, len(content), 'firefox_sqlite', content, sources)

def _readin_moz_places(file):
	"""Reads in a file of the SQLite format created by Mozilla Firefox.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	con = lite.connect(file)
	content = []
	with con:
		cur = con.cursor()
		cur.execute("SELECT moz_historyvisits.id, moz_places.url, datetime(moz_historyvisits.visit_date/1000000,'unixepoch'), * FROM moz_places, moz_historyvisits WHERE moz_places.id = moz_historyvisits.place_id;")
		rows = cur.fetchall()
		sources = []
		counter = 0
		for row in rows:
			_print_progress(counter)
			counter += 1
			date = datetime.datetime.strptime(row[2],"%Y-%m-%d %H:%M:%S")
			source = ''
			pattern = re.compile(r'.*(www\.|http[s]{0,1}:\/\/)([^\.]+)\..*')
			m = pattern.match(row[1])
			if m:
				source = m.group(2)
				if not source in sources:
					sources.append(source)
			content.append(logfile_entry(row[0], file, row[1], row[3:], date, '',source))
		_delete_print()
	return logfile(file, len(content), 'firefox_sqlite', content, sources)

def _readin_evtx(file):
	"""Reads in a file of the evtx format created by Microsoft Windows.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	content = []
	unparsed_entries = 0
	with evtx.Evtx(file) as log:
		c = 0
		sources = []
		for record in log.records():
			c += 1
			print('parse log file entry nr: {}'.format(c),end='\r')
			try:
				obj = untangle.parse(record.xml())#untangle can produce an OSError on Windows, since Windows uses a different format for timestamps
			except OSError:
				c -= 1
				unparsed_entries += 1
				continue
			curr_obj = obj.Event.System
			date = datetime.datetime.strptime(curr_obj.TimeCreated['SystemTime'],"%Y-%m-%d %H:%M:%S.%f")
			full_line = record.xml()
			if hasattr(curr_obj,'Provider'):
				source = curr_obj.Provider['Name']
			else:
				source = ''
			if ( (not source in sources) or (not sources == '')):
				sources.append(source)
			line_nr = curr_obj.EventRecordID.cdata
			content.append(logfile_entry(int(line_nr), file, curr_obj.EventID.cdata, full_line, date, curr_obj.Computer.cdata, source))
		_delete_print()
	if unparsed_entries > 0:
		print('Unfortunately, {} entries could not be parsed. Please see the documentation'.format(unparsed_entries))
		print()
	return logfile(file, len(content), 'evtx', content, sources)
#END internal functions

#START exported functions
def readin(file, time_offset='+0000'):
	"""Reads in a file and stores the content.
	Returns a logfileclasses.logfile object containg all the data.
	This function only checks if the file extension or the file name suits to one it might be able to parse.
	It then chooses the respective function to parse the file and calls it.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	p = re.compile(r'^.*log$')
	if p.match(file):
		return _readin_syslog(file, time_offset)
	else:
		p2 = re.compile(r'^.*\.slogviz\.json$')
		if p2.match(file):
			return _readin_JSON(file)
		else:
			p3 = re.compile(r'^.*History$')
			if p3.match(file):
				return _readin_chrome_history(file)
			else:
				p4 = re.compile(r'^.*places.*\.sqlite$')
				if p4.match(file):
					return _readin_moz_places(file)
				else:
					p5 = re.compile(r'^.*\.evtx$')
					if p5.match(file):
						return _readin_evtx(file)
					else:
						return None
#END exported functions