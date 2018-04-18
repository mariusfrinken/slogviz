import re
from datetime import timedelta

def the_first_50(list_of_entries):
	return list_of_entries[0:50]


def the_last_50(list_of_entries):
	return list_of_entries[-50:]

def log_in_rule(list_of_entries):
	ret = []
	found_log_in = 0
	found_log_off = 0
	p = re.compile(r'^pam_unix\(sudo:session\):\ssession\sopened\sfor\suser\sroot.*$')
	p2 = re.compile(r'^pam_unix\(sudo:session\):\ssession\sclosed\sfor\suser\sroot.*$')
	for x in list_of_entries:
		if p.match(x.message):
			found_log_in += 1
			if found_log_in > found_log_off + 1:
				ret.append(x)
				found_log_in -= 1
		elif p2.match(x.message):
			found_log_off += 1
			if found_log_off > found_log_in:
				ret.append(x)
				found_log_off -= 1
	return ret

def _P(x):
	return x.message == "event A" and x.origin_name == "a.log"

def _Q(x):
	return x.message == "event A" and x.origin_name == "b.log"

def _G(x,y):
	return abs((x.timestamp - y.timestamp).total_seconds()) <= 5

def eventA_rule_break(list_of_entries):
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

