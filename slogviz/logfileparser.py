# -*- coding: utf-8 -*-
import re
import datetime
import json
import sqlite3 as lite
import sys
import Evtx.Evtx as evtx
import Evtx.Views as e_views
import untangle

from .logfileclasses import *



"""Reads in a file and stores the content.
Returns a logfile Object containg all the data."""
def readin(file):


	#
	p = re.compile(r'^.*\.evtx$')
	if p.match(file):
		return readin_evtx(file)
	#
	p = re.compile(r'^.*log$')
	if p.match(file):
		return readin_syslog(file)
	else:
		p2 = re.compile(r'^.*\.slogviz\.json$')
		if p2.match(file):
			return readin_JSON(file)
		else:
			p3 = re.compile(r'^History$')
			if p3.match(file):
				return readin_chrome_history(file)
			else:
				p4 = re.compile(r'^places\.sqlite$')
				if p4.match(file):
					return readin_moz_places(file)
				else:
					print('file format not supported')
					return None


"""Reads in a file of the syslog format."""
def readin_syslog(file):
	f = open(file, 'r')
	counter = 0
	content = []
	sources = []
	p = re.compile(r'^(\D{3,3}\s+\d+\s\d{2,2}:\d{2,2}:\d{2,2})\s(\S+)\s([^\][:]+)(\[\d+\]){0,1}([^:])*:\s(.*)$')
	for x in f.readlines():
		counter+=1
		m = p.search(x)
		if not m:
			p2 = re.compile(r'^.*---\slast\smessage\srepeated\s\d+\stime[s]{0,1}\s---$')
			if p2.search(x):
				counter -= 1
				continue
			#print(x)
			content[-1].message += x
			content[-1].full_line += x
			counter -= 1
			continue
		formatted_date = datetime.datetime.strptime("2017 " + m.group(1),"%Y %b %d %H:%M:%S")
		#formatted_date = datetime.datetime.strptime(m.group(1),"%b %d %H:%M:%S")
		content.append(logfile_entry(counter,m.group(6),m.group(0),formatted_date,m.group(2),m.group(3)))
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

def readin_chrome_history(file):
	con = lite.connect(file)
	content = []
	with con:
		cur = con.cursor()
		cur.execute("SELECT *, datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), 'unixepoch') FROM urls;")
		rows = cur.fetchall()
		for row in rows:
			date = datetime.datetime.strptime(row[-1],"%Y-%m-%d %H:%M:%S")
			content.append(logfile_entry(row[0], row[1], ", ".join(str(x) for x in row), date, '','chrome'))
	return logfile(file, len(content), 'firefox_sqlite', content, ['chrome'])


def readin_moz_places(file):
	con = lite.connect(file)
	content = []
	with con:
		cur = con.cursor()
		cur.execute("SELECT *, datetime(last_visit_date/1000000 , 'unixepoch') FROM moz_places;")
		rows = cur.fetchall()
		for row in rows:
			date = datetime.datetime.strptime(row[-1],"%Y-%m-%d %H:%M:%S")
			content.append(logfile_entry(row[0], row[1], row, date, '','firefox'))
	return logfile(file, len(content), 'firefox_sqlite', content, ['firefox'])



def readin_evtx(file):
	content = []
	with evtx.Evtx(file) as log:
		c = 0
		for record in log.records():
			c += 1
			print('parse record nr: {}'.format(c),end='\r')
			obj = untangle.parse(record.xml())
			curr_obj = obj.Event.System
			date = datetime.datetime.strptime(curr_obj.TimeCreated['SystemTime'],"%Y-%m-%d %H:%M:%S.%f")
			full_line = record.xml()
			if hasattr(curr_obj,'Provider'):
				source = curr_obj.Provider['Name']
			else:
				source = ''
			line_nr = curr_obj.EventRecordID.cdata

			content.append(logfile_entry(int(line_nr), curr_obj.EventID.cdata, full_line, date, curr_obj.Computer.cdata, source))
	sources = {}
	for x in content:
		if len(x.source) > 0:
			sources[x.source] = 1
	return logfile(file, len(content), 'evtx', content, [x for x in sources.keys()])

