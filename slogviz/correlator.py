import re
import datetime
from logfileclasses import *


def mock_rule(list_of_entries): #doubles are not elimanted
	ret = []
	for x in list_of_entries:
		for y in list_of_entries:
			if x.line_nr != y.line_nr and y not in ret and x.full_line == y.full_line:
				ret.append(x)
				ret.append(y)
	if not ret:
		return []
	else:
		return ["{} on line {}".format(x.full_line,x.line_nr) for x in ret]

def log_rule(list_of_entries):
	ret = []
	found_log_in = 0
	found_log_off = 0
	p = re.compile(r'^.*session opened for user kurt.*$')
	p2 = re.compile(r'^.*session closed for user kurt.*$')
	for x in list_of_entries:
		if p.match(x.message):
			found_log_in += 1
			if found_log_in > found_log_off + 1:
				ret.append(" on line {} there are too many logins".format(x.line_nr))
				found_log_in -= 1
		elif p2.match(x.message):
			found_log_off += 1
			if found_log_off > found_log_in:
				ret.append(" on line {} there are too many logoff".format(x.line_nr))
				found_log_off -= 1
	return ret



def inX(x):
	p = re.compile(r'^.*session.*lightdm.*$')
	return p.search(x.full_line)
def inY(y):
	p = re.compile(r'.*Session.*lightdm.*')
	return p.search(y.full_line)
def inBoth(x,y):
	return (x.date - y.date) <= datetime.timedelta(seconds=30) and (x.date - y.date) >= datetime.timedelta(seconds=0)

def mock_rule_mult(logfiles):
	if len(logfiles) == 2:
		satisfies = []
		broken_x = {x.line_nr:x for x in logfiles[0].content if inX(x)}
		broken_y = {y.line_nr:y for y in logfiles[1].content if inY(y)}
		for x in list(broken_x.keys()):
			for y in list(broken_y.keys()):
				xv = broken_x[x]
				yv = broken_y[y]
				if inBoth(xv,yv):
					satisfies.append((xv,yv))
					del broken_x[x]
					del broken_y[y]
		return (broken_x.values(),broken_y.values(),satisfies)
	else:
		return None


def correlate_single_file(logfile, rules):
	ret = find_broken(logfile.content, rules)
	for x in ret:
		print(x)

def find_broken(list,rules):
	ret = [item for x in rules for item in x(list)]
	return ret


def correlate_multiple_files(logfiles,rules):
	(xl,yl,sl) = find_broken(logfiles, rules)
	print("broken from file 1: ")
	for x in xl:
		print(x.full_line )
	print("broken from file 2: ")
	for y in yl:
		print(y.full_line )
	print("The rules are satisfied by: ")
	for (x,y) in sl:
		print(x.full_line + " and " + y.full_line)


