import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import send_from_directory
import os

def generate_table(x,text,lines, max_rows=100):
	return html.Table(
		# Header
		[html.Tr([html.Th('id'),html.Th('full_line')])] +

		# Body
		[html.Tr([html.Td(x[i]),html.Td(text[i])]) for i in range(0,min(lines, max_rows))]
	)




def webview_run(logfiles):

	checklist = []
	valuelist = []
	for x in logfiles:
		for y in x.sources:
			checklist.append({'label': "{} -> {}".format(x.name,y), 'value': y})
			#valuelist.append(y)

	app = dash.Dash()
	app.css.config.serve_locally = True
	app.scripts.config.serve_locally = True
	#my_css_url = './my.css'
	#app.css.append_css({'external_url': my_css_url})
	y_r,x_r,a_r,y_w,x_w,a_w = logfiles[0].give_plot_data_scatter()
	xa = [x_r,x_w]
	ya = [y_r,y_w]
	aa = [a_r,a_w]
	max_size = max(max(a_r, default=10), max(a_w, default=10))
	if a_w == []:
		amount = 1
	else:
		amount = 2

	app.layout = html.Div(children=[
		html.Link(
		rel='stylesheet',
		href='/static/stylesheet.css'
		),
		html.Div('Assets loading locally'),
		html.H1(children='Hello, Welcome to SLogVIZ'),
		dcc.Graph(
			id='test'
		),
		html.Div([
			dcc.RadioItems(
				id='remove_redundant_entries',
				options=[{'label': 'Keep', 'value': 0},{'label': 'Remove', 'value': 1}],
				value=0,
				labelStyle={'display': 'inline-block'}
			)
		]),
		html.H4(children=logfiles[0].name),
		html.Div([
			html.H4('Here are the Sources'),
			dcc.Checklist(
				id='sources',
				options=checklist,
				values=valuelist,
				labelStyle={'display': 'inline-table'}
			)
		], style={'max-height': '200px', 'max-width': '400px', 'overflow-y': 'scroll'}),
				dcc.Graph(
			id='test2',
			figure={
				'data': [
	                go.Scatter(
	                    x = xa[i],
	                    y = ya[i],
	                    text=aa[i],
	                    mode='markers',
	                    opacity=0.7,
	                    marker=dict(
	                        size = aa[i],
	                        sizeref = 5*max_size/(20**2),
	                        sizemin = 4
	                  	),
	                    line={
	                        'width': 0.5
	                        #'color' : 'black'
	                        #'line': {'width': 0.5, 'color': 'black'}
	                    },
	                    name=i
	                ) for i in range(0,amount)
	            ],
	            'layout': go.Layout(
	                xaxis={'title': 'X'},
	                yaxis={'title': 'Y'},
	                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
	                legend={'x': 0, 'y': 1},
	                hovermode='closest',
					height= 800
	            )
	        }
		),
		#html.Div(id='tabelle')
	])

	@app.callback(
		dash.dependencies.Output('test', 'figure'),
		[dash.dependencies.Input('remove_redundant_entries', 'value'),
		dash.dependencies.Input('sources', 'values')
		])
	def update_graph(remove_boolean, sources):

		x_list = {}
		y_list = {}
		text_list = {}
		for i in logfiles:
			_, y_list[i.name], x_list[i.name], text_list[i.name] = i.give_plot_dataP(remove_redundant_entries=remove_boolean, sources=sources)
		return {
				'data': [
		                go.Scatter(
		                    x = x_list[i.name],
		                    y = y_list[i.name],
		                    text = text_list[i.name] ,
		                    textposition = 'bottom',
		                    mode = 'lines+markers',
		                    opacity = 0.7,
		                    marker = {
		                        'size': 5,
		                        'line': {'width': 0.5}
		                    },
		                    line = {
		                        'width': 2
		                        #'color' : 'black'
		                        #'line': {'width': 0.5, 'color': 'black'}
		                    },
		                    name = i.name
		                ) for i in logfiles
				],
				'layout': go.Layout(
		                xaxis={'title': 'Dates'},
		                yaxis={'title': 'Lines'},
		                margin={'l': 80, 'b': 40, 't': 10, 'r': 10},
		                legend={'x': 1, 'y': 1},
		                hovermode='closest'
				)
		}
	# @app.callback(
	# 	dash.dependencies.Output('tabelle', 'children'),
	# 	[dash.dependencies.Input('remove_redundant_entries', 'value'),
	# 	dash.dependencies.Input('sources', 'values')
	# 	])
	# def update_table(remove_boolean, sources):
	# 	newsources = [x for x in valuelist if x not in sources]
	# 	_,x,_,text = logfiles[0].give_plot_dataP(remove_redundant_entries=remove_boolean ,sources=newsources)
	# 	lines = len(x)
	# 	return generate_table(x,text,lines)

	@app.server.route('/static/<path:path>')
	def static_file(path):
		static_folder = os.path.join(os.getcwd(), 'static')
		return send_from_directory(static_folder, path)

	app.run_server()


