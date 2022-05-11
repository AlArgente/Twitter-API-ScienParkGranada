import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from utils_app import generate_table
from utils_db import query_db
from utils import format_time_sql

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
bootstrap_theme=[dbc.themes.BOOTSTRAP]
darkly = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=bootstrap_theme)
app.title = 'Real-Time Twitter Monitor'
# TODO: Define layouts and callbacks
# server = app.server
# app.run_server() # To run the server

df = query_db(table_attributes=['text', 'user_name', 'created_at', 'polarity'])
df['created_at'] = df['created_at'].apply(lambda x: format_time_sql(x))

app.layout = html.Div(children=[
    html.H2('Monitorización de Twitter en tiempo real'),
    generate_table(df=df, max_rows=20),
    dcc.Interval(id='interval-component-slow',
                 interval=30000, # 300000, # In miliseconds. 300000 = 5 minutes.
                 n_intervals=0),
    # Here add more Divs to the layout
    html.Br(),
    html.Div(id='live-update-graph'),
    html.Div(id='live-update-bottom-graph')
], className="dash-bootstrap")

@app.callback(Output('live-update-graph', 'children'),
              [Input('interval-component-slow', 'n_intervals')])
def update_graph_live(n):
    # First load data and prepare data to show in the layout
    data_from = "Twitter. Hashtag: #Eurovision, #FelizMiércoles"

    # Positives, negatives and neutral comments.
    df = query_db(table_attributes=['text', 'user_name', 'created_at', 'polarity'])
    df['created_at'] = df['created_at'].apply(lambda x: format_time_sql(x))
    num_pos = df[df['polarity']==1]['polarity'].count()
    num_neg = df[df['polarity']==-1]['polarity'].count()
    num_neu = df[df['polarity']==0]['polarity'].count()
    # Create the graph once data is loaded
    children = [
        html.Div([
            html.Div([
                dcc.Graph(
                    id='pie-chart',
                    figure={
                        'data': [
                            go.Pie(
                                labels=['Positivos', 'Negativos', 'Neutros'],
                                values=[num_pos, num_neg, num_neu],
                                name='Polaridad',
                                marker_colors=['rgba(184, 247, 212, 0.6)','rgba(255, 50, 50, 0.6)','rgba(131, 90, 241, 0.6)'],
                                textinfo='value',
                                hole=.65
                            )
                        ],
                        'layout': {
                            'showLeyend':False,
                            'title':'Tuits en los últimos 10 minutos',
                            'annotations':[
                                dict(
                                    text='{0:.1f}K'.format((num_pos+num_neg+num_neu)/1000),
                                    font=dict(
                                        size=40
                                    ),
                                    showarrow=False
                                )
                            ]
                        }
                    }
                )
            ], style={'width': '27%', 'display': 'inline-block'})
        ])
    ]
    return children

if __name__ == '__main__':
    app.run_server(debug=True)