import dash
import webbrowser
import dash_core_components as dcc
import dash_html_components as html
import base64

from threading import Timer
from ht_analysis.datautils import DataHelper
from plotly import graph_objects as go
from warnings import filterwarnings
filterwarnings('ignore')


def open_browser(port):
    webbrowser.open_new(f'http://127.0.0.1:{port}/')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app_color = {"graph_bg": "#ffd5cc", "graph_line": "#007ACE"}

dh = DataHelper()
res = dh.get_gw_pl_superset()
axes_choice = list(sorted(set(res.columns)))
pl_name = 'Kevin De Bruyne'

image_filename = 'Resources/Small Alt Lion Angry Red Crown Black Outline.jpg'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# To change the page background color:
# app.layout = html.Div(style={'backgroundColor': app_color['graph_bg']},children=[
app.layout = html.Div([
    html.Div([
            html.Div(
                [
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
                ],style={'display': 'inline-block'}),
                
            html.Div(
                [
                html.H4("FPL Viz & Solver Tool"),
                html.P(
                    "Plot your next FPL transfer. Literally.")
                ],style={'display': 'inline-block'}),
        ]),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='dropdown-axis1',
                options=[{'label': i, 'value': i} for i in axes_choice],
                value='value_gw'
            )
        ],
        style={'width': '14%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='dropdown-axis2',
                options=[{'label': i, 'value': i} for i in 
                         axes_choice],
                value='total_points_gw'
            )
        ], style={'width': '14%', 'float': 'centre', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='dropdown-axis3',
                options=[{'label': i, 'value': i} for i in 
                         axes_choice],
                value='',
                placeholder = 'Axis 3 (Optional)',
            )
        ], style={'width': '14%', 'float': 'centre', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='dropdown-position',
                options=[{'label': i, 'value': i} for i in list(sorted(set(res['position'])))],
                value = '',
                placeholder = 'Pos'
            )
        ], style={'width': '11%', 'float': 'centre', 'display': 'inline-block'}),
    
        html.Div([
            dcc.Dropdown(
                id='dropdown-gw',
                options=[{'label': i, 'value': i} for i in list(sorted(set(res['round'])))],
                value = max(res['round'])
            )
        ], style={'width': '8%', 'float': 'centre', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='dropdown-team',
                options=[{'label': i, 'value': i} for i in list(sorted(set(res['team'])))],
                value = '',
                placeholder = 'Team(s)',
                multi=True
            )
        ], style={'width': '36%', 'float': 'centre', 'display': 'inline-block'}),
    
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='main-scatter',
            clear_on_unhover=False,
            hoverData={'points': [{'customdata': pl_name}]}
        )
    ], style={'width': '60%', 'height': '100%', 'display': 'inline-block',
              'padding': '0 20'}),
    
    html.Div([
        dcc.Graph(id='timeseries-1'),
        dcc.Graph(id='timeseries-2'),
    ], style={'display': 'inline-block', 'width': '39%'}),
    
    html.Div([
        dcc.Graph(id='timeseries-3')
    ], style={'display': 'inline-block', 'width': '39%'}),

    # html.Div(id='hover-value-main-scatter', style={'display': 'none'}),

    # html.Div(id='sub-df', style={'display': 'none'}),
])

@app.callback(
    dash.dependencies.Output('main-scatter', 'figure'),
    [dash.dependencies.Input('dropdown-axis1', 'value'),
      dash.dependencies.Input('dropdown-axis2', 'value'),
      dash.dependencies.Input('dropdown-axis3', 'value'),
      dash.dependencies.Input('dropdown-gw', 'value'),
      dash.dependencies.Input('dropdown-team', 'value'),
      dash.dependencies.Input('dropdown-position', 'value'),
      ])
def update_main_scatter_graph(axis1, axis2, axis3, gw, team, position):
    cols_to_pull = ['player_name','team', 'position', axis1, axis2]
    if axis3: cols_to_pull.append(axis3)
    sub_df = res[cols_to_pull].loc[res['round']==gw]
    if team:
        sub_df = sub_df.loc[sub_df['team'].isin(team)]
    if position:
        sub_df = sub_df.loc[sub_df['position'] == position]
    traces = []
    titletext = f"{axis1} vs {axis2} - GW {gw}"
    if axis3:
        titletext = f"{axis1} vs {axis2} vs {axis3}- GW {gw}"
        traces.append(go.Scatter3d(x=sub_df[axis1],
                                    y=sub_df[axis2],
                                    z=sub_df[axis3],
                                    text=sub_df['player_name'], 
                                    mode='markers',
                                    marker={
                                    'size': 10,
                                    'opacity': 0.3,
                                    'color': '#4d4fb1',
                                    'line': {'width': 2, 'color': '#240059'}
                                    },
                                    customdata=sub_df['player_name']),
                      )
    else:
        traces.append(go.Scatter(x=sub_df[axis1],
                                    y=sub_df[axis2],
                                    text=sub_df['player_name'], 
                                    mode='markers',
                                    marker={
                                    'size': 10,
                                    'opacity': 0.3,
                                    'color': '#4d4fb1',
                                    'line': {'width': 2, 'color': '#240059'}
                                    },
                                    customdata=sub_df['player_name']),
                      )
    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': axis1,'type': 'linear'},
            yaxis={'title': axis2,'type': 'linear'},
            zaxis={'title': axis3,'type': 'linear'},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            legend={'xanchor':"center",
                'yanchor':"top",
                'y':-0.15,
                'x':0.5,
                'orientation':'h'},
            height=450,
            hovermode='closest',
            title={'text': f"{axis1} vs {axis2} - GW {gw}",
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )
    }

@app.callback(
    dash.dependencies.Output('timeseries-1', 'figure'),
    [dash.dependencies.Input('main-scatter', 'hoverData')])
def update_top_timeseries(hdata):
    pl_name = hdata['points'][0]['customdata']
    pl_df = res.loc[res['player_name'] == pl_name].reset_index(drop=True)
    title = pl_name
    traces = []
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['total_points_gw'],
        mode='lines+markers',
        color='#5269d1',
        name='Total Pts',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#5269d1',
            'line': {'width': 2, 'color': '#5269d1'}}))
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['minutes_gw'],
        mode='lines+markers',
        color='#6ec0ff',
        name='Mins Played',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#6ec0ff',
            'line': {'width': 2, 'color': '#6ec0ff'}},
        yaxis = 'y2'))
    return {
        'data': traces,
        'layout': {
            'height': 225,
            'margin': {'l': 40, 'b': 30, 'r': 40, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'xaxis': {'showgrid': False},
            'yaxis1': {'title': 'pts', 'side':'left', 'titlefont': {'color': '#5269d1'}},
            'yaxis2': {'title': 'mins pl', 'side':'right', 'overlaying': 'y', 'titlefont': {'color': '#6ec0ff'}},
            'legend' : {'xanchor':"center",
                'yanchor':"top",
                'y':-0.15,
                'x':0.5,
                'orientation':'h'},}
    }

@app.callback(
    dash.dependencies.Output('timeseries-2', 'figure'),
    [dash.dependencies.Input('main-scatter', 'hoverData')])
def update_second_timeseries(hdata):
    pl_name = hdata['points'][0]['customdata']
    pl_df = res.loc[res['player_name'] == pl_name].reset_index(drop=True)
    traces = []
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['goals_scored_gw'],
        mode='lines+markers',
        color='#5269d1',
        name='Goals',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#5269d1',
            'line': {'width': 2, 'color': '#5269d1'}}))
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['assists_gw'],
        mode='lines+markers',
        color='#990e1c',
        name='Assists',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#990e1c',
            'line': {'width': 2, 'color': '#990e1c'}}))
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['clean_sheets_gw'],
        mode='markers',
        color='#3a55c9',
        name='Clean Sheet',
        marker={
            'size': 3,
            'opacity': 1,
            'color': '#3a55c9',
            'line': {'width': 2, 'color': '#3a55c9'}},
        yaxis = 'y2'))
    return {
        'data': traces,
        'layout': {
            'height': 225,
            'margin': {'l': 40, 'b': 30, 'r': 40, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)'
            }],
            'xaxis': {'showgrid': False},
            'yaxis1': {'title': 'Goals / Assists', 'side':'left', 'titlefont': {'color': '#5269d1'}},
            'yaxis2': {'title': 'Clean Sheet', 'side':'right', 'overlaying': 'y', 'titlefont': {'color': '#3a55c9'}},
            'legend' : {'xanchor':"center",
                'yanchor':"top",
                'y':-0.15,
                'x':0.5,
                'orientation':'h'},}
    }

@app.callback(
    dash.dependencies.Output('timeseries-3', 'figure'),
    [dash.dependencies.Input('main-scatter', 'hoverData')])
def update_second_timeseries(hdata):
    pl_name = hdata['points'][0]['customdata']
    pl_df = res.loc[res['player_name'] == pl_name].reset_index(drop=True)
    traces = []
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['transfers_in_gw'],
        mode='lines+markers',
        color='#5269d1',
        name='Transfers In',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#5269d1',
            'line': {'width': 2, 'color': '#5269d1'}}))
    traces.append(dict(
        x = pl_df['round'],
        y = pl_df['transfers_out_gw'],
        mode='lines+markers',
        color='#990e1c',
        name='Transfers Out',
        marker={
            'size': 1,
            'opacity': 0.7,
            'color': '#990e1c',
            'line': {'width': 2, 'color': '#990e1c'}}))
    return {
        'data': traces,
        'layout': {
            'height': 225,
            'margin': {'l': 40, 'b': 10, 'r': 40, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)'
            }],
            'xaxis': {'title': 'GW', 'showgrid': False},
            'yaxis1': {'title': 'Transfers', 'side':'left', 'titlefont': {'color': '#5269d1'}},
            'legend' : {'xanchor':"center",
                'yanchor':"top",
                'y':-0.15,
                'x':0.5,
                'orientation':'h'},}
    }

if __name__ == '__main__':
    port = '8050'
    # Timer(2, open_browser(port)).start();
    # app.run_server(port=port, debug=False, dev_tools_hot_reload=False)
    app.run_server(debug=True, use_reloader=False)

__doc__ = """
app.py is a plotly dash dashboard - built to solve the FPL problem
=======================================================================
Hridai Trivedy 2022.
"""