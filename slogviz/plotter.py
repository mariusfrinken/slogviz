# -*- coding: utf-8 -*-

"""The sub module of slogviz that takes care of producing matplotlib plots.

Exported functions:

"""

import matplotlib.pyplot as plt

from datetime import timedelta
from matplotlib.dates import DateFormatter

#from .logfileclasses import *
# this import is not necessary because of the overall structure, but keep in mind that classes and functions defined there are used here

#START internal functions
def _transform_select_string(select_string, logfile):
	selected_sources = []
	tmp = select_string.split(',')
	for s in tmp:
		if s in logfile.sources and s not in selected_sources:
			selected_sources.append(s)
	if len(selected_sources) == 0:
		selected_sources = logfile.sources
	return selected_sources

def _quit_figure(event):
	"""Helper function for closing pyplot windows with the 'q' key"""
	if event.key == 'q':
		plt.close(event.canvas.figure)
#END internal functions

def show():
	"""Finally produces one ore multiple pyplot plots.
	Has to be called once after one calling any of the other public functions in order to see a plot.
	"""
	plt.show()

#START plots
def plot_single(log, remove_redundant_entries, select_string):
	"""Plots the Data from one logfile onto one system of coordinates"""
	selected_sources = _transform_select_string(select_string,log)
	plot_data , lines, dates, _ = log.give_plot_data(remove_redundant_entries=remove_redundant_entries, sources=selected_sources)
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	l, = plt.plot(dates,lines,picker=10, color='red', marker='.', linestyle='-', linewidth=0.5, ms=5, mec='blue', label=log.name )
	myFmt = DateFormatter("%Y %d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	plt.title('Analysis of the file \"'+log.name+'\"')
	plt.legend(loc='upper left')
	plt.subplots_adjust(left=0.1, bottom=0.23, right=0.9, top=0.95)
	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)
	ax.set_xlabel('timestamp')
	ax.set_ylabel('sequential id')

	def update_annot(ind):
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		if remove_redundant_entries == 1:
			text = plot_data[y[ind["ind"][0]]-1]
		else:
			temp = [x for x in plot_data if x.id == y[ind["ind"][0]]]
			text = temp[0]
		annot.set_text(text)
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			cont, ind = l.contains(event)
			if cont:
				update_annot(ind)
				annot.set_visible(True)
				fig.canvas.draw_idle()
			else:
				if vis:
					annot.set_visible(False)
					fig.canvas.draw_idle()

	fig.canvas.mpl_connect("motion_notify_event", hover)
	fig.canvas.mpl_connect('key_press_event', _quit_figure)

def plot_single_file_multiple_sources(log, remove_redundant_entries, select_string):
	"""
	"""
	selected_sources = _transform_select_string(select_string,log)

	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	plot_data, _ , _ , _ = log.give_plot_data(remove_redundant_entries=remove_redundant_entries)
	color_map = plt.get_cmap('gnuplot2')
	color_index = [color_map(1.*i/len(selected_sources)) for i in range(0,len(selected_sources))]
	ax.set_prop_cycle(color=color_index)

	ls = []
	counter = 0
	for s in selected_sources:
		dates = [x.timestamp for x in plot_data if x.source == s]
		if remove_redundant_entries == 1:
			lines = [plot_data.index(x) for x in plot_data if x.source == s]
		else:
			lines = [x.id for x in plot_data if x.source == s]
		breakline_s = s
		if len(breakline_s) >= 23:
			for i in range(0,int(len(breakline_s)/23)):
				breakline_s = breakline_s[:22] + '\n' + breakline_s[22:]
		tmp, = ax.plot(dates,lines, label=breakline_s,marker='.', linestyle='None', linewidth=0.05, ms=10, picker=10)
		ls.append(tmp)
		counter += 1
	myFmt = DateFormatter("%d.%b %H:%M")

	ax.xaxis.set_major_formatter(myFmt)

	plt.legend(loc='upper left', bbox_to_anchor=(0, 0.95), bbox_transform=plt.gcf().transFigure)

	annot = ax.annotate("", xy=(0,0), xytext=(0.23,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)
	ax.set_xlabel('timestamp')
	if remove_redundant_entries == 1:
		ax.set_ylabel('number of sequential entry')
		plt.title('Analysis of the files ' + log.name +'\n' + 'where all entries having the same timestamp are removed')
		plt.subplots_adjust(left=0.3, bottom=0.23, right=0.95, top=0.90)
	else:
		plt.title('Analysis of the files ' + log.name)
		ax.set_ylabel('sequential id')
		plt.subplots_adjust(left=0.3, bottom=0.23, right=0.95, top=0.95)

	def update_annot(l,ind):
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		if remove_redundant_entries == 1:
			text = plot_data[y[ind["ind"][0]]]
		else:
			temp = [x for x in plot_data if x.id == y[ind["ind"][0]]]
			text = temp[0]
		annot.set_text(text)
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			for l in ls:
				cont, ind = l.contains(event)
				if cont:
					update_annot(l,ind)
					annot.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if vis:
						annot.set_visible(False)
						fig.canvas.draw_idle()

	fig.canvas.mpl_connect("motion_notify_event", hover)
	cid = plt.gcf().canvas.mpl_connect('key_press_event', _quit_figure)

def plot_multiple_timeline(logs):
	"""Plots the Data from logs onto one system of coordiantes"""
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	c = 0
	line2D_array = []
	plot_data_dict = {}
	for l in logs:
		plot_data, _, dates, _ = l.give_plot_data()
		tmp, = ax.plot(dates, [c]*len(dates), label=l.name, picker=4, marker='.', linestyle='-', linewidth=0.05, ms=5)
		plot_data_dict[tmp.get_c()] = plot_data
		line2D_array.append(tmp)
		c += 1
	myFmt = DateFormatter("%Y %d.%b %H:%M")
	ax.xaxis.set_major_formatter(myFmt)
	ax.set_yticks(range(0,len(logs)))
	ax.set_yticklabels([x.name for x in logs])
	names = ' and '.join([x.name for x in logs])
	plt.title('Analysis of the files ' + names)
	t = 0.15+(0.1)*len(logs)
	#plt.legend(bbox_to_anchor=(0.25, t+0.1), bbox_transform=plt.gcf().transFigure)
	plt.subplots_adjust(left=0.23, bottom=0.2, right=0.9, top=t)

	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)
	ax.set_xlabel('timestamps')
	ax.set_ylabel('log files')

	def update_annot(l,ind):
		plot_data = plot_data_dict[l.get_c()]
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		text = plot_data[ind["ind"][0]]
		annot.set_text(text)
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			for l in line2D_array:
				cont, ind = l.contains(event)
				if cont:
					update_annot(l,ind)
					annot.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if vis:
						annot.set_visible(False)
						fig.canvas.draw_idle()

	fig.canvas.mpl_connect("motion_notify_event", hover)
	cid = plt.gcf().canvas.mpl_connect('key_press_event', _quit_figure)

def plot_multiple(logs, remove_redundant_entries, select_string):
	"""Plots the Data from logs onto one system of coordiantes"""

	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	line2D_array = []
	plot_data_dict = {}
	for l in logs:
		selected_sources = _transform_select_string(select_string,l)
		pld, lines, dates, _ = l.give_plot_data(remove_redundant_entries=remove_redundant_entries, sources=selected_sources)
		tmp, = ax.plot(dates, lines, label=l.name, picker=4, marker='.', linestyle='-', linewidth=0.5, ms=3.5)
		line2D_array.append(tmp)
		plot_data_dict[tmp.get_c()] = pld
	myFmt = DateFormatter("%Y %d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	names = ' and '.join([x.name for x in logs])
	if remove_redundant_entries:
		plt.title('Analysis of the files ' + names +'\n' + 'where all entries having the same timestamp are removed')
		plt.subplots_adjust(left=0.1, bottom=0.18, right=0.9, top=0.90)
	else:
		plt.title('Analysis of the files ' + names)
		plt.subplots_adjust(left=0.1, bottom=0.18, right=0.9, top=0.95)

	plt.legend()

	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)
	ax.set_xlabel('timestamp')
	ax.set_ylabel('sequential id')

	def update_annot(l,ind):
		plot_data = plot_data_dict[l.get_c()]
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		if remove_redundant_entries == 1:
			text = plot_data[y[ind["ind"][0]]-1]
		else:
			temp = [x for x in plot_data if x.id == y[ind["ind"][0]]]
			text = temp[0]
		annot.set_text(text)
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			for l in line2D_array:
				cont, ind = l.contains(event)
				if cont:
					update_annot(l,ind)
					annot.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if vis:
						annot.set_visible(False)
						fig.canvas.draw_idle()

	fig.canvas.mpl_connect("motion_notify_event", hover)


	cid = plt.gcf().canvas.mpl_connect('key_press_event', _quit_figure)

def scatter_plot(log, frame_seconds=-1):
	if frame_seconds == -1:
		frame_seconds = (log.content[-1].timestamp - log.content[0].timestamp).total_seconds() / timedelta(seconds=100).total_seconds()
	lines,dates,areas = log.give_plot_data_bar(frame_seconds=frame_seconds)
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	myFmt = DateFormatter("%Y %d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	ax.set_xlabel('timestamp')
	ax.set_ylabel('amount of entries')
	plt.title('Analysis of the file \"'+log.name+'\" \n with frame size ' + str(frame_seconds) +' seconds')

	width = timedelta(seconds=frame_seconds).total_seconds() / timedelta(days=1).total_seconds()
	normal = ax.bar(dates, areas, width, label='entries', edgecolor='k')

	plt.legend()
	plt.subplots_adjust(left=0.15, bottom=0.2, right=0.9, top=0.9)
	cid = fig.canvas.mpl_connect('key_press_event', _quit_figure)


def superplot(logs,remove_redundant_entries,select_string):
	for l in logs:
		scatter_plot(l)
		plot_single(l,remove_redundant_entries,select_string)
		plot_single_file_multiple_sources(l, remove_redundant_entries, select_string)
	plot_multiple(logs,remove_redundant_entries,select_string)
	plot_multiple_timeline(logs)
	show()


def plot_correlated(list_of_entries, logfiles, rule_name):
	plot_data = list_of_entries
	plot_data.sort(key=lambda x: x.id)

	dates = {}
	ids = {}
	plot_data_dict = {}
	for log in logfiles:
		dates[log.name] = [x.timestamp for x in plot_data if x.origin_name == log.name]
		ids[log.name] = [x.id for x in plot_data if x.origin_name == log.name]

	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()

	line2D_array = []
	counter = 0
	for log in logfiles:
		tmp, = plt.plot(dates[log.name],[counter]*len(dates[log.name]),picker=10, marker='.', linestyle='None', linewidth=0.5, ms=10, label=log.name )
		line2D_array.append(tmp)
		plot_data_dict[tmp.get_c()] = log.name
		counter += 1
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)

	names = ' and '.join([x.name for x in logfiles])
	plt.title('Correlation of files ' + names + '\n with rule ' + rule_name )
	#plt.legend()
	t = 0.15+(0.1)*len(logfiles)
	plt.subplots_adjust(left=0.23, bottom=0.2, right=0.9, top=t)
	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)
	ax.set_xlabel('timestamp')
	ax.set_yticks(range(0,len(logfiles)))
	ax.set_yticklabels([x.name for x in logfiles])

	def update_annot(l, ind):
		origin_name = plot_data_dict[l.get_c()]
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		temp = [x for x in plot_data if x.id == ids[origin_name][ind["ind"][0]] and x.origin_name == origin_name]
		text = temp[0]
		annot.set_text(text)
		annot.get_bbox_patch().set_alpha(0.4)

	def hover(event):
		vis = annot.get_visible()
		if event.inaxes == ax:
			for l in line2D_array:
				cont, ind = l.contains(event)
				if cont:
					update_annot(l,ind)
					annot.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if vis:
						annot.set_visible(False)
						fig.canvas.draw_idle()

	fig.canvas.mpl_connect("motion_notify_event", hover)
	fig.canvas.mpl_connect('key_press_event', _quit_figure)



#END plots