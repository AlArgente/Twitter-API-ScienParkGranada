import dash
from dash import html
import pandas as pd
from utils_app import generate_table
from utils_db import query_db

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Real-Time Twitter Monitor'
# TODO: Define layouts and callbacks
# server = app.server
# app.run_server() # To run the server

df = query_db(table_attributes=['text', 'polarity', 'user_name', 'created_at'])
df['created_at'] = pd.to_datetime(df['created_at'])

app.layout = html.Div([
    html.H4(children="Test info:"),
    generate_table(df=df, max_rows=10)
])

if __name__ == '__main__':
    app.run_server(debug=True)