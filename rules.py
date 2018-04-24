"""
This file is an example for how SLogVIZ can correlate log file entries.
In order to define your own correlation rule, simply add a function, that takes a list of entries,
and returns a subset of them.
The returned list is meant to represent all entries that are interesting, meaning they are in some way correlated, consistent or
inconsistent.

In order to be usable by SLogVIZ, the names of a rule function must not start with an underscore.

In this file, there are three sample rules:
	the_first_50_entries
	the_last_50_entries
	eventA_rule_break
"""

from datetime import timedelta

def the_first_50_entries(list_of_entries):
	"""Simply returns the first 50 entries."""
	return list_of_entries[0:50]

def the_last_50_entries(list_of_entries):
	"""Simply returns the last 50 entries."""
	return list_of_entries[-50:]

def _P(x):
	"""Helper function.
	returns True when x has a certain message and origin_name
	"""
	return x.message == "event A" and x.origin_name == "a.log"

def _Q(x):
	"""Helper function.
	returns True when x has a certain message and origin_name
	"""
	return x.message == "event A" and x.origin_name == "b.log"

def _G(x,y):
	"""Helper function.
	returns True when the timestamps of x and y are within 5 seconds."""
	return abs((x.timestamp - y.timestamp).total_seconds()) <= 5

def eventA_rule_break(list_of_entries):
	"""
	This correlation function returns all entries in the list_of_entries, that have the message "event A",
	the origin_name "a.log" and no counterpart with the same message with the origin_name "a.log" within 5 seconds and vice versa.
	"""
	ret = []
	for x in list_of_entries:
		if _P(x):
			found = False
			for y in list_of_entries:
				if _Q(y) and _G(x,y):
					found = True
					break
			if not found:
				ret.append(x)
		elif _Q(x):
			found = False
			for y in list_of_entries:
				if _P(y) and _G(x,y):
					found = True
					break
			if not found:
				ret.append(x)
	return ret

