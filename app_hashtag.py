import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from dash_extensions.enrich import Output as OutputExt
from dash_extensions.enrich import Input as InputExt
import plotly.graph_objs as go
import pandas as pd

from utils_app import generate_table, generate_timeline_user, generate_pie_chart, generate_pie_chart_less
from utils_db import query_db, query_db_last_minutes, query_total_tweets
from utils import format_time_sql

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
bootstrap_theme=[dbc.themes.BOOTSTRAP]
darkly = [dbc.themes.DARKLY]
cosmo = [dbc.themes.COSMO]
cyborg = [dbc.themes.CYBORG]
solar = [dbc.themes.SOLAR]
# app = dash.Dash(__name__) # , external_stylesheets=solar)
app = DashProxy(__name__, prevent_initial_callbacks=True, transforms=[MultiplexerTransform()]) # , external_stylesheets=solar)
app.config.external_stylesheets=bootstrap_theme
app.title = 'Real-Time Twitter Monitor'
# TODO: Define layouts and callbacks
# server = app.server
# app.run_server() # To run the server

app.layout = html.Div(children=[
    html.H2('Monitorización de Twitter en tiempo real'),
    dcc.Interval(id='interval-component-slow',
                 interval=30000, # 300000, # In miliseconds. 300000 = 5 minutes.
                 n_intervals=0),
    # Here add more Divs to the layout
    html.Br(),
    html.Div(id='live-update-graph'),
    html.Div(id='live-update-bottom-graph'),
    dcc.Input(id='input-1-state', type='text', value='Usuario'),
    html.Button(id='submit-button-state-user', n_clicks=0, children='Submit user'),
    dcc.Input(id='input-2-state', type='text', value='Hashtag'),
    html.Button(id='submit-button-state-hashtag', n_clicks=0, children='Submit hashtag'),
    html.Div(id='output-state'),
]) # , className="dash-bootstrap")

@app.callback(Output('live-update-graph', 'children'),
              [Input('interval-component-slow', 'n_intervals')])
def update_graph_live(n):
    print("Aquí estoy!")
    # First load data and prepare data to show in the layout
    data_from = "Twitter. Hashtag: #Eurovision, #FelizMiércoles"
    total_tweets = query_total_tweets()
    # Create the graph once data is loaded
    children = [
        generate_table(),
        html.Div([
            generate_timeline_user("DaSCI_es"),
            generate_timeline_user("ParqueCiencias"),
            # generate_pie_chart_less(num_neg=num_neg, num_neu=num_neu, num_pos=num_pos),
            generate_pie_chart(days="all"),
            generate_pie_chart(days=5)
        ])
    ]
    return children

@app.callback(OutputExt('output-state', 'children'),
              InputExt('submit-button-state-user', 'n_clicks'),
              State('input-1-state', 'value'))
def update_output_with_username(n_clicks_user, input_user):
    return f'''
        The user button has been pressed {n_clicks_user} times,
        and the user value is {input_user}.
    '''

@app.callback(OutputExt('output-state', 'children'),
              InputExt('submit-button-state-hashtag', 'n_clicks'),
              State('input-2-state', 'value'))
def update_output_with_hashtag(n_clicks_hashtag, input_hashtag):
    return f'''
        The hashtag button
        has been pressed {n_clicks_hashtag} and the hashtah
        value is {input_hashtag}.
    '''


if __name__ == '__main__':
    app.run_server(debug=True)