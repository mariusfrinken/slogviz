import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
from logfileclasses import *
from datetime import timedelta

def transform_select_string(select_string, logfile):
	selected_sources = []
	tmp = select_string.split(',')
	for s in tmp:
		if s in logfile.sources:
			selected_sources.append(s)
		elif s:
			print("{} does not contain an entry from the source: '{}'".format(logfile.name,s))
	if len(selected_sources) == 0:
		selected_sources = logfile.sources
	return selected_sources

def quit_figure(event):
	"""Helper function for closing pyplot windows with the 'q' key"""
	if event.key == 'q':
		plt.close(event.canvas.figure)

def show():
	plt.show()

def plot_single(log,remove_redundant_entries, selected_sources):
	"""Plots the Data from one logfile onto one system of coordinates"""
	plot_data , lines, dates, _ = log.give_plot_dataP(remove_redundant_entries=remove_redundant_entries, sources=selected_sources)
	if remove_redundant_entries==1:
		msize = 10
	else:
		msize=5

	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	l, = plt.plot(dates,lines,picker=10, color='red', marker='.', linestyle='-', linewidth=0.5, ms=msize, mec='blue', label=log.name )
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	plt.title('Analysis of the file \"'+log.name+'\"')
	plt.legend()
	plt.subplots_adjust(left=0.18, bottom=0.1, right=0.9, top=0.9)
	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)

	def update_annot(ind):
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		#text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), " ".join(["n" for n in ind["ind"]]))
		#text = " \n".join([plot_data[n-1].__str__() for n in ind["ind"]])
		text = plot_data[ind["ind"][0]]
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

	fig.canvas.mpl_connect('key_press_event', quit_figure)
	#cid = plt.gcf().canvas.mpl_connect('pick_event', on_pick)


def plot_single_file_multiple_sources(log,selected_sources):
	""""""
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	plot_data, _ , _ , _ = log.give_plot_dataP()

	ls = []
	for s in selected_sources:
		dates = [x.date for x in plot_data if x.source == s]
		lines = [x.line_nr for x in plot_data if x.source == s]
		tmp, = ax.plot(dates,lines, label=s,marker='.', linestyle='None', linewidth=0.05, ms=10)
		ls.append(tmp)
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	plt.title('Analysis of the files ' + log.name)
	plt.legend(bbox_to_anchor=(1, 0.8), bbox_transform=plt.gcf().transFigure)
	plt.subplots_adjust(left=0.18, bottom=0.1, right=0.8, top=0.9)
	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)

	def update_annot(l,ind):
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		text = plot_data[y[ind["ind"][0]]-1]
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
	cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)



def plot_multiple_timeline(logs,remove_redundant_entries, select_string):
	"""Plots the Data from logs onto one system of coordiantes"""
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	c = 0
	line2D_array = []
	plot_data_dict = {}
	for l in logs:
		selected_sources = transform_select_string(select_string, l)
		plot_data, _, dates, _ = l.give_plot_dataP(remove_redundant_entries=remove_redundant_entries, sources=selected_sources)
		tmp, = ax.plot(dates, [c]*len(dates),label=l.name,picker=4,marker='.', linestyle='-', linewidth=0.05, ms=5)
		plot_data_dict[tmp.get_c()] = plot_data
		line2D_array.append(tmp)
		c += 1
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	ax.set_yticks([0,1])
	ax.set_yticklabels([x.name for x in logs])
	names = ' and '.join([x.name for x in logs])
	plt.title('Analysis of the files ' + names)
	t = 0.15+(0.1)*len(logs)
	#plt.legend(bbox_to_anchor=(0.25, t+0.1), bbox_transform=plt.gcf().transFigure)
	plt.subplots_adjust(left=0.18, bottom=0.15, right=0.9, top=t)

	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)

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


	cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)


def plot_multiple(logs, remove_redundant_entries, select_string):
	"""Plots the Data from logs onto one system of coordiantes"""

	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	line2D_array = []
	plot_data_dict = {}
	for l in logs:
		selected_sources = transform_select_string(select_string,l)
		pld, lines, dates, _ = l.give_plot_dataP(remove_redundant_entries=remove_redundant_entries, sources=selected_sources)
		tmp, = ax.plot(dates, lines, label=l.name)
		line2D_array.append(tmp)
		plot_data_dict[tmp.get_c()] = pld
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	names = ' and '.join([x.name for x in logs])
	plt.title('Analysis of the files ' + names)
	plt.legend()
	plt.subplots_adjust(left=0.18, bottom=0.1, right=0.9, top=0.9)

	annot = ax.annotate("", xy=(0,0), xytext=(0.01,0.01) ,textcoords='figure fraction', bbox=dict(boxstyle="round", fc="cyan"), arrowprops=dict(arrowstyle="->"))
	annot.set_visible(False)

	def update_annot(l,ind):
		plot_data = plot_data_dict[l.get_c()]
		x,y = l.get_data()
		annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
		text = plot_data[y[ind["ind"][0]]-1]
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


	cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)

def scatter_plot(log):
	lines,dates,areas,out_of_order_lines, out_of_order_dates, out_of_order_areas = log.give_plot_data_scatter()
	fig, ax = plt.subplots(figsize=(11,7))
	fig.autofmt_xdate()
	#normal = ax.scatter(dates,lines,s=[2.5*x for x in areas],label=log.name, picker=True)
	# out_of_order = ax.scatter(out_of_order_dates,out_of_order_lines,s=[2.5*x for x in out_of_order_areas],label='out of order lines',picker=True)
	myFmt = DateFormatter("%d.%b %H:%M:%S")
	ax.xaxis.set_major_formatter(myFmt)
	# xmin = min(dates + out_of_order_dates)
	# xmax = max(dates + out_of_order_dates)
	# plt.xlim(xmin-timedelta(minutes=100),xmax+timedelta(minutes=100))
	# plt.title('Analysis of the file \"'+log.name+'\"')


	width = 0.009
	normal = ax.bar(dates, areas, width, color='y', label='normal lines')
	if out_of_order_dates:
		out_of_order = ax.bar(out_of_order_dates , out_of_order_areas, width, color='r',label='out of order lines')

	def autolabel(rects):
		for rect in rects:
			height = rect.get_height()
			ax.text(rect.get_x() + rect.get_width()/2., 1.05*height, '%d' % int(height), ha='center', va='bottom')

	#autolabel(normal)
	#autolabel(out_of_order)

	plt.legend()
	plt.subplots_adjust(left=0.18, bottom=0.1, right=0.9, top=0.9)
	cid = fig.canvas.mpl_connect('key_press_event', quit_figure)


def superplot(logs,remove_redundant_entries,select_string):
	for l in logs:
		selected_sources = transform_select_string(select_string,l)
		scatter_plot(l)
		plot_single(l,remove_redundant_entries,selected_sources)
		plot_single_file_multiple_sources(l,selected_sources)
	plot_multiple(logs,remove_redundant_entries,select_string)
	plot_multiple_timeline(logs,remove_redundant_entries,select_string)
	show()