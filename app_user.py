import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from utils_app import generate_table
from utils_db import query_db, query_db_last_minutes
from utils import format_time_sql

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
bootstrap_theme=[dbc.themes.BOOTSTRAP]
darkly = [dbc.themes.DARKLY]
app = dash.Dash(__name__, external_stylesheets=bootstrap_theme)
app.title = 'Real-Time Twitter Monitor for username'