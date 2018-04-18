# -*- coding: utf-8 -*-

""" This sub module defines the logfile and logfile_entry classes.
All functions defined in this module are considered private, they are not invoked by any other module of slogviz.
"""

import datetime
import json
import collections

#START internal functions
def _give_dates(array):
	return [x.timestamp for x in array]

def _give_full_lines(array):
	return [x.structured_data for x in array]

def _give_messages(array):
	return [x.message for x in array]

def _give_ids(array, remove_redundant_entries):
	if remove_redundant_entries == 1:
		return [x for x in range(1,len(array)+1)] #TODO!!!!
	else:
		return [x.id for x in array]

def select_entries_param(array, param):
	if not param or len(param) == 0:
		return [x for x in array]
	return [x for x in array if x.source in param]
#END internal functions


class logfile_entry(object):
	"""A class for storing one single log file entry
	"""
	def __init__(self, id, origin_name, message, structured_data, timestamp, hostname, source):
		self.id = id
		self.origin_name = origin_name
		self.message = message
		self.structured_data = structured_data
		self.timestamp = timestamp
		self.hostname = hostname
		self.source = source

	def __str__(self):
		return 'Entry {0.id} at {0.timestamp} from hostname {0.hostname} and source {0.source} with the message:\n {0.message}'.format(self)

class logfile(object):
	"""A class for storing content and meta data of one log file
	"""
	def __init__(self, name, lines, type, content, sources):
		self.name = name
		self.lines = lines
		self.type = type
		self.content = content
		self.sources = sources

	def __str__(self):
		return 'File of the type {0.type} with the name {0.name} and {0.lines} lines'.format(self)

	def give_plot_data(self, remove_redundant_entries=0, sources=[]):
		"""Filters the entries in the self.content attribute and returns the filtered list, their respective ids, timestamps and messages.
		All list returned are sorted by the id of their respective log file entry.

		Keyword arguments:
		remove_redundant_entries -- If set to 1, all entries with the same timestamp will be condensed to one (default 0)
		sources -- A list of sources, entries not in this list will be filtered out. If this list is empty, no filtering will occur. (default [])
		"""
		ret = []
		if remove_redundant_entries:
			ret = self.remove_redundant_entries()
		else:
			ret = self.content
		ret = select_entries_param(ret,sources)
		ret.sort(key=lambda x: x.id)
		return ret, _give_ids(ret, remove_redundant_entries), _give_dates(ret), _give_messages(ret)

	def remove_redundant_entries(self):
		"""Returns the self.content list, where all entries will have different timestamps.
		This is achieved by keeping the first occurrence of each timestamp.
		"""
		dict = {x: self.content[x] for x in range(0,self.lines)}
		oldvalue= None
		for counter in range(0,self.lines):
			v = dict[counter]
			if counter>1 and oldvalue == v.timestamp:
				del dict[counter]
			oldvalue=v.timestamp
		return [v for k,v in dict.items()]

	def give_plot_data_bar(self, frame_seconds=0):
		"""Counts how many entries in self.content in frames of the size frame_seconds exist and returns three lists.
		The first list is an ascending list of all found frames ([1,2,3,...n] where n is the amount of found frames).
		The second list stores the timestamp of the beginning of each frame in the first list.
		The third list represents the amounts of entries in the frames of the first list ([99,10,2,...] would mean that in frame 1 there are 99 entries).

		Keyword arguments:
		frame_seconds -- the size of each time frame in seconds (default 0)
		"""
		dict = collections.OrderedDict()
		oldvalue = None
		counter = 1
		ret = []
		time_delta = datetime.timedelta(seconds=frame_seconds)

		for v in self.content:
			if oldvalue and v.timestamp - oldvalue <= time_delta:
				dict[oldvalue] += 1
			else:
				dict[v.timestamp] = 1
				oldvalue = v.timestamp
				ret.append(counter)
				counter += 1
		return ret,list(dict.keys()),[v for k,v in dict.items()]

	def export_to_JSON(self, sparse=False):
		"""Stores the log file object as an JSON file with the name <self.name>.slogviz.json
		The file created by this function can use up to 5 times the space the original file took, therefore there is the sparse argument.

		Keyword arguments:
		sparse -- if set to True, the self.structured_data not stored inside the JSON file in order to save space (default False)
		"""
		class CustomEncoder(json.JSONEncoder):
			def default(self, o):
				try:
					if sparse:
						o.structured_data = ''
				except AttributeError:
					pass
				if isinstance(o, datetime.datetime):
					return {'datetime': o.replace().isoformat()}
				if isinstance(o, str):
					return json.JSONEncoder.default(self,o)
				return {'{}'.format(o.__class__.__name__): o.__dict__}
		pathname='{}.slogviz.json'.format(self.name)
		ret = open(pathname,'w')
		json.dump(self, ret, indent=4, cls=CustomEncoder)
		ret.close()
