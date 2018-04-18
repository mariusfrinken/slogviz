# -*- coding: utf-8 -*-

import platform
import re
import datetime
import time
import json
import sqlite3 as lite
import Evtx.Evtx as evtx
import untangle

from .logfileclasses import *



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
	if not platform.system() == "Windows":
		print('\x1b[2K\x1b[1A'*number)

def readin(file):
	"""Reads in a file and stores the content.
	Returns a logfileclasses.logfile object containg all the data.
	This function only checks if the file extension suits to one it might be able to parse.
	It then chooses the respective function to parse the file and calls it.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	p = re.compile(r'^.*log$')
	if p.match(file):
		return readin_syslog(file)
	else:
		p2 = re.compile(r'^.*\.slogviz\.json$')
		if p2.match(file):
			return readin_JSON(file)
		else:
			p3 = re.compile(r'^.*History$')
			if p3.match(file):
				return readin_chrome_history(file)
			else:
				p4 = re.compile(r'^.*places.*\.sqlite$')
				if p4.match(file):
					return readin_moz_places(file)
				else:
					p5 = re.compile(r'^.*\.evtx$')
					if p5.match(file):
						return readin_evtx(file)
					else:
						return None

def readin_syslog(file):
	"""Reads in a file of the syslog format.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
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
			formatted_date = datetime.datetime.strptime("2018 " + m.group(1),"%Y %b %d %H:%M:%S")
			content.append(logfile_entry(counter, file, m.group(6), m.group(0), formatted_date, m.group(2),m.group(3)))
			if not m.group(3) in sources:
				sources.append(m.group(3))
		elif p2.search(x):
			counter -= 1
		else:
			m3 = precise_date.search(x)
			if m3:
				unformatted_date = m3.group(1)
				unformatted_date = unformatted_date[:-3]+unformatted_date[-2:]
				formatted_date = datetime.datetime.strptime(unformatted_date,"%Y-%m-%dT%H:%M:%S.%f%z")
				content.append(logfile_entry(counter, file, m3.group(6), m3.group(0), formatted_date, m3.group(2), m3.group(3)))
				if not m3.group(3) in sources:
					sources.append(m3.group(3))
			else:
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

def readin_JSON(file):
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
				date = datetime.datetime.strptime(unformatted_date,"%Y-%m-%dT%H:%M:%S.%f%z")
			return logfile_entry(obj['logfile_entry']['id'], file, obj['logfile_entry']['message'], obj['logfile_entry']['structured_data'], date,obj['logfile_entry']['hostname'],obj['logfile_entry']['source'])
		return obj

	fp = open(file,'r')
	lf = json.load(fp, object_hook=object_decoder)
	fp.close()
	return lf

def readin_chrome_history(file):
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

def readin_moz_places(file):
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

def readin_evtx(file):
	"""Reads in a file of the evtx format created by Microsoft Windows.
	Returns a logfileclasses.logfile object containg all the data.

	Positional arguments:
	file -- the name of the file to readin as a string, here name euqals path to the file
	"""
	content = []
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
	return logfile(file, len(content), 'evtx', content, sources)

