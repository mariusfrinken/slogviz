# -*- coding: utf-8 -*-

import datetime
import json
import collections

def give_dates(array):
	return [x.date for x in array]

def give_full_lines(array):
	return [x.full_line for x in array]

def select_entries_param(array,param):
	if not param or len(param) == 0:
		return [x for x in array]
	return [x for x in array if x.source in param]



class logfile_entry(object):
	"""\
	A class for storing one single logfile entry"""
	def __init__(self, line_nr, message, full_line, date, hostname, source):
		self.line_nr = line_nr
		self.full_line = full_line
		self.message = message
		self.date = date
		self.hostname = hostname
		self.source = source
	def __str__(self):
		return 'Entry {0.line_nr}: {0.full_line}'.format(self)

class logfile(object):
	"""\
	A class for storing content and meta data"""
	def __init__(self, name, lines, type, content, sources):
		self.name = name
		self.lines = lines
		self.type = type
		self.content = content
		self.sources = sources
	def __str__(self):
		return 'File of the type {0.type} with the name {0.name} and {0.lines} lines'.format(self)

	def give_plot_dataP(self, remove_redundant_entries=0, sources=[]):
		ret = []
		if remove_redundant_entries:
			ret = self.remove_redundant_entries()
		else:
			ret = self.content
		ret = select_entries_param(ret,sources)

		return ret, [x for x in range(1,len(ret)+1)], give_dates(ret), give_full_lines(ret)

	def remove_redundant_entries(self):
		dict = {x: self.content[x] for x in range(0,self.lines)}
		oldvalue= None
		for counter in range(0,self.lines):
			v = dict[counter]
			if counter>1 and oldvalue == v.date:
				del dict[counter]
			oldvalue=v.date
		return [v for k,v in dict.items()]

	def select_entries(self,param):
		return [x for x in self.content if x.source==param]

	# def give_plot_data_scatter(self): # what happens when the first element is out of order
	# 	dict = collections.OrderedDict()
	# 	out_of_order_dict = collections.OrderedDict()
	# 	oldvalue = None
	# 	counter = 1
	# 	lines = []
	# 	out_of_order_lines = []

	# 	for v in self.content:
	# 		if oldvalue and oldvalue == v.date:
	# 			dict[v.date] += 1
	# 			oldvalue=v.date
	# 		elif v.date in dict.keys() or (oldvalue and v.date < oldvalue):
	# 			if v.date in out_of_order_dict.keys():
	# 				out_of_order_dict[v.date] += 1
	# 			else:
	# 				out_of_order_dict[v.date] = 1
	# 				out_of_order_lines.append(counter)
	# 				counter += 1
	# 		else:
	# 			dict[v.date] = 1
	# 			oldvalue=v.date
	# 			lines.append(counter)
	# 			counter += 1
	# 	return lines,list(dict.keys()),[v for k,v in dict.items()],out_of_order_lines,list(out_of_order_dict.keys()),[v for k,v in out_of_order_dict.items()]
	def give_plot_data_scatter(self): # what happens when the first element is out of order
		dict = collections.OrderedDict()
		out_of_order_dict = collections.OrderedDict()
		oldvalue = None
		counter = 1
		lines = []
		out_of_order_lines = []
		time_delta = datetime.timedelta(seconds=60)

		for v in self.content:
			if oldvalue and oldvalue <= v.date and v.date - oldvalue <= time_delta:
				dict[oldvalue] += 1
			# elif oldvalue and oldvalue < v.date and v.date and v.date - oldvalue > time_delta:
			# 	dict[v.date] = 1
			# 	oldvalue = v.date
			elif v.date in dict.keys() or (oldvalue and v.date < oldvalue):

				if v.date in out_of_order_dict.keys():
					out_of_order_dict[v.date] += 1
				else:
					out_of_order_dict[v.date] = 1
					#print("put in {} because {}".format(v.date, oldvalue))
					out_of_order_lines.append(counter)
					counter += 1
			else:
				dict[v.date] = 1
				oldvalue = v.date
				lines.append(counter)
				counter += 1
		return lines,list(dict.keys()),[v for k,v in dict.items()],out_of_order_lines,list(out_of_order_dict.keys()),[v for k,v in out_of_order_dict.items()]

	def export_to_JSON(self):
		class CustomEncoder(json.JSONEncoder):
			def default(self, o):
				if isinstance(o, datetime.datetime):
					return {'datetime': o.replace(microsecond=0).isoformat()}
				if isinstance(o, str):
					return json.JSONEncoder.default(self,o)
				return {'{}'.format(o.__class__.__name__): o.__dict__}
		pathname='{}.json'.format(self.name)
		ret = open(pathname,'w')
		json.dump(self, ret, indent=4,cls=CustomEncoder)
		ret.close()
