import dash
from dash import html, dcc
import pandas as pd
from utils_app import generate_table
from utils_db import query_db

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Real-Time Twitter Monitor'
# TODO: Define layouts and callbacks
# server = app.server
# app.run_server() # To run the server

df = query_db(table_attributes=['text', 'user_name', 'created_at', 'polarity'])
df['created_at'] = pd.to_datetime(df['created_at'])

app.layout = html.Div(children=[
    html.H2('Real-Time Twitter Monitoring'),
    generate_table(df=df, max_rows=20),
    dcc.Interval(id='interval-component-slow',
                 interval=30000, # 300000, # In miliseconds. 300000 = 5 minutes.
                 n_intervals=0)
    # Here add more Divs to the layout
])

if __name__ == '__main__':
    app.run_server(debug=True)