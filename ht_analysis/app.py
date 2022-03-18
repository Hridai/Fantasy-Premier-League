__doc__ = """
curve_fitter_app.py is a plotly dash dashboard which allows hyperparameter tweaking
============================================================
Choose the existing curve and the country for which it has been fitted on for a
date and tweak the hyperparameters to see how the curve would behave.
Note: The outlier detection methods do not work as of yet as the developer
ran out of time, and would definitely reccommend this be finished. The alpha
and l1_ratio parameters are the pertinent ones.
The initial hyperparameters for each curves are read from the ModelHyperparameters
table.
"""
from warnings import filterwarnings
filterwarnings('ignore')
from threading import Timer
from ht_analysis.datautils import DataHelper
import dash
import numpy as np # CAN REMOVE THIS?
from datetime import datetime
from ht_analysis.statutils import StatUtil
import webbrowser
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd


def open_browser(port):
    webbrowser.open_new(f'http://127.0.0.1:{port}/')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dh = DataHelper()
res = dh.get_gw_pl_superset()
axes_choice = list(sorted(set(res.columns)))

# axes_choice = ['player_name', 'assists_pl', 'bonus_pl', 'bps_pl', 'clean_sheets_pl', 
#                'creativity_pl', 'element_pl', 'fixture_pl', 'goals_conceded_pl', 
#                'goals_scored_pl', 'ict_index_pl', 'influence_pl', 'kickoff_time_pl', 
#                'minutes_pl', 'opponent_team_pl', 'own_goals_pl', 'penalties_missed_pl', 
#                'penalties_saved_pl', 'red_cards_pl', 'round', 'saves_pl', 'selected_pl', 
#                'team_a_score_pl', 'team_h_score_pl', 'threat_pl', 'total_points_pl', 
#                'transfers_balance_pl', 'transfers_in_pl', 'transfers_out_pl', 
#                'value_pl', 'was_home_pl', 'yellow_cards_pl', 'name', 'position', 
#                'team', 'xP', 'assists_gw', 'bonus_gw', 'bps_gw', 'clean_sheets_gw', 
#                'creativity_gw', 'element_gw', 'fixture_gw', 'goals_conceded_gw', 
#                'goals_scored_gw', 'ict_index_gw', 'influence_gw', 'kickoff_time_gw', 
#                'minutes_gw', 'opponent_team_gw', 'own_goals_gw', 'penalties_missed_gw', 
#                'penalties_saved_gw', 'red_cards_gw', 'saves_gw', 'selected_gw', 
#                'team_a_score_gw', 'team_h_score_gw', 'threat_gw', 'total_points_gw', 
#                'transfers_balance_gw', 'transfers_in_gw', 'transfers_out_gw', 
#                'value_gw', 'was_home_gw', 'yellow_cards_gw', 'GW']

alpha_marks = {-3: '0.001',-2: '0.01',-1: '0.1',0: '1',0.5: '5',1: '10',
                2: '100'}
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app_color = {"graph_bg": "#ffd5cc", "graph_line": "#007ACE"}

# To change the page background color:
# app.layout = html.Div(style={'backgroundColor': app_color['graph_bg']},children=[
app.layout = html.Div([
    html.Div([
            html.Div(
                [
                html.H4("Curve Calibration Dashboard"),
                html.P(
                    "A dashboard which will let you re-model existing curves " \
                    "by tweaking model hyperparameters and outlier parameters."
                ),],
            ),
        ]),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='dropdown-axis1',
                options=[{'label': i, 'value': i} for i in axes_choice],
                value='value_gw'
            )
        ],
        style={'width': '22%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='dropdown-axis2',
                options=[{'label': i, 'value': i} for i in 
                         axes_choice],
                value='total_points_gw'
            )
        ], style={'width': '22%', 'float': 'centre', 'display': 'inline-block'}),
    
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
            id='crossfilter-indicator-scatter'
        )
    ], style={'width': '60%', 'height': '100%', 'display': 'inline-block',
              'padding': '0 20'}),
    
    html.Div([
        html.H4("Hyperparameters"),
        html.Plaintext("Alpha"),
        dcc.Slider(
            id='slider-alpha',
            marks=alpha_marks,
            min=-3,
            max=2,
            step=None,
            value = -2
        ),
        html.Plaintext("L1 Ratio"),
        dcc.Slider(
            id='slider-l1-ratio',
            min = 0,
            max = 1,
            value = 0.,
            marks={0: '0', 0.1: '0.1', 0.2: '0.2', 0.3: '0.3', 0.4: '0.4',
                0.5: '0.5',0.6: '0.6',0.7: '0.7',0.8: '0.8',0.9: '0.9',
                1: '1',
            },
            # marks={"{:.1f}".format(score): "{:.1f}".format(score) for score
            # in np.linspace(0,1,11)}, # no work.
            step=0.1
        ),
        html.Plaintext("Polynomial Degree"),
        dcc.Slider(
            id='slider-polynomial-degree',
            min = 1,
            max = 10,
            value = 3,
            marks={1: '1',2: '2',3: '3',4: '4',5: '5',6: '6',7: '7',8: '8',
                9: '9',10: '10',
            },
            step=1
        ),
        html.H4('Outlier Parameters'),
        html.Plaintext("X Axis Threshold"),
        dcc.Slider(
            id='slider-outlier-x-axis-threshold',
            min = 0,
            max = 4,
            value = 1,
            marks={0: '0',0.5: '0.5',1: '1',1.5: '1.5',2: '2',2.5: '2.5',
                3: '3',3.5: '3.5',4: '4'},
            step=0.5
        ),
        html.Plaintext("Std Error Threshold"),
        dcc.Slider(
            id='slider-std-error-threshold',
            min = 0,
            max = 3,
            value = 2.,
            marks={0: '0',0.5: '0.5',1: '1',1.5: '1.5',2: '2',2.5: '2.5',
                3: '3'},
            step=0.5
        ),
        html.Plaintext("DBScan EPS"),
        dcc.Slider(
            id='slider-dbscan-eps',
            min = 0,
            max = 5,
            value = 2,
            marks={0: '0',1: '1',2: '2',3: '3',4: '4',5: '5'},
            step=1
        ),
        html.Plaintext("DBScan Min Samples"),
        dcc.Slider(
            id='slider-dbscan-min-samples',
            min = 0,
            max = 6,
            value = 2,
            marks={0: '0',1: '1',2: '2',3: '3',4: '4',5: '5',6: '6'},
            step=1
        ),
        dcc.Checklist(
        options=[
                {'label': 'Parametric', 'value': 'outlier_parametric'},
                {'label': 'DBSCAN', 'value': 'outlier_dbscan'},
                {'label': 'X Axis Threshold', 'value': 'outlier_xthreshold'},
                {'label': 'Contamination', 'value': 'outlier_contamination'}
            ],
        value=['outlier_parametric', 'outlier_contamination'],
        labelStyle={'display': 'inline-block', 'padding': '30 50'},
        inputStyle={"margin-left": "20px"}
        ),
        # html.Button('Run', id='btn-run', n_clicks=0, 
        #             style={'margin-left': '1px'}),
        # html.Button('Reset', id='btn-reset', style={'background-color':'#b31200',
        #                                             'color':'white',
        #                                             'margin-left': '5px'}),
    ], style={'display': 'inline-block', 'width': '40%',
              'height': '100%',"verticalAlign": "top"}),

    html.Div(id='sub-df', style={'display': 'none'}),
])

@app.callback(
    dash.dependencies.Output('adj-hyperparams-df', 'children'),
   [dash.dependencies.Input('slider-alpha', 'value'),
     dash.dependencies.Input('slider-l1-ratio', 'value'),
     dash.dependencies.Input('slider-polynomial-degree', 'value'),
     dash.dependencies.Input('slider-outlier-x-axis-threshold', 'value'),
     dash.dependencies.Input('slider-std-error-threshold', 'value'),
     dash.dependencies.Input('slider-dbscan-eps', 'value'),
     dash.dependencies.Input('slider-dbscan-min-samples', 'value'),
     ])
def load_adjusted_hyperparameters(alpha, l1ratio, polydeg, xaxisthresh,
                                  stderrorthresh, dbscaneps, dbscanminsamples):
    adjusted_hyperparams_dict = {
        'alpha' : alpha_marks.get(alpha),
        'l1_ratio' : l1ratio,
        'polynomial_degree' : polydeg,
        'x_axis_threshold' : xaxisthresh,
        'std_error_threshold' : stderrorthresh,
        'dbscan_eps' : dbscaneps,
        'dbscan_min_samples' : dbscanminsamples,
        }
    df_res = pd.DataFrame(adjusted_hyperparams_dict.values(), 
                          index = adjusted_hyperparams_dict.keys())
    return df_res.to_json(orient='split')
              
# @app.callback(
    # [dash.dependencies.Output('full-df', 'children')],
    # [dash.dependencies.Input('dropdown-axis1', 'value'),
    #   dash.dependencies.Input('dropdown-axis2', 'value'),
    #   dash.dependencies.Input('dropdown-gw', 'value')
    #   ])
# def load_dataframes(curvename, country, date):
    # dh = DataHelper()
    # res = dh.get_gw_pl_superset()
    # return res.to_json(orient='split')

@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('dropdown-axis1', 'value'),
      dash.dependencies.Input('dropdown-axis2', 'value'),
      dash.dependencies.Input('dropdown-gw', 'value'),
      dash.dependencies.Input('dropdown-team', 'value'),
      dash.dependencies.Input('dropdown-position', 'value'),
      ])
def update_main_scatter_graph(axis1, axis2, gw, team, position):
    sub_df = res[['player_name','team', 'position', axis1, axis2]].loc[res['round']==gw]
    print(team)
    if team:
        sub_df = sub_df.loc[sub_df['team'].isin(team)]
    if position:
        sub_df = sub_df.loc[sub_df['position'] == position]
    traces = []
    traces.append(go.Scatter(x=sub_df[axis1],
                                y=sub_df[axis2],
                                text=sub_df['player_name'], 
                                mode='markers',
                                marker={
                    'size': 11,
                    'opacity': 0.3,
                    'color': '#4d4fb1',
                    'line': {'width': 2, 'color': '#240059'}
                }))
    return {
        'data': traces,
        'layout': dict(
            xaxis={
                'title': axis1,'type': 'linear'},
            yaxis={
                'title': axis2,'type': 'linear'},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            legend={'xanchor':"center",
                'yanchor':"top",
                'y':-0.15,
                'x':0.5,
                'orientation':'h'},
            height=450,
            hovermode='closest',
            clickmode='event+select',
            title={'text': f"{axis1} vs {axis2} - GW {gw}",
                'y':0.98,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )
    }

if __name__ == '__main__':
    port = '8050'
    Timer(2, open_browser(port)).start();
    app.run_server(port=port, debug=False, dev_tools_hot_reload=False)