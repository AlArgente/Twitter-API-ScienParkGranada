import dash
import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from utils_app import generate_table, generate_timeline_user, generate_pie_chart

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
bootstrap_theme = [dbc.themes.BOOTSTRAP]
darkly = [dbc.themes.DARKLY]
cosmo = [dbc.themes.COSMO]
cyborg = [dbc.themes.CYBORG]
solar = [dbc.themes.SOLAR]
app = DashProxy(__name__, prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()])
app.config.external_stylesheets = bootstrap_theme
app.title = 'Sent-IA'
app.layout = html.Div(children=[
    html.H2('Sent-IA', style={"text-align": "center", 'padding-top':'1em', 'margin-bottom':'-1em'}),
    dcc.Interval(id='interval-component-slow',
                 # interval=1.8e+6,# 30 minutes
                 interval=10000,  # For testing
                 n_intervals=0),
    html.Br(),
    html.Div(id='live-update-graph'),
    html.Div(id='live-update-bottom-graph'),
    html.Div(id='output-state'),
])

emoji_csv = pd.read_csv('descriptions_of_emojis.csv', sep=';')
happy_emoji = emoji_csv['Native'].loc[emoji_csv['Description'] == 'GRINNING FACE'].values[0]
neutral_emoji = emoji_csv['Native'].loc[emoji_csv['Description'] == 'NEUTRAL FACE'].values[0]
negative_emoji = emoji_csv['Native'].loc[emoji_csv['Description'] == 'PENSIVE FACE'].values[0]
emojis = {'Positivo': happy_emoji,
          'Negativo': negative_emoji,
          'Neutro': neutral_emoji
          }
del emoji_csv

@app.callback(Output('live-update-graph', 'children'),
              [Input('interval-component-slow', 'n_intervals')])
def update_graph_live(n):
    children = [
        generate_table(emojis=emojis),
        html.Div([
            generate_timeline_user("DaSCI_es"),
            generate_timeline_user("ParqueCiencias"),
            generate_pie_chart(days="all"),
            generate_pie_chart(days=5)
        ], style={
            'padding-top': '2em',
        }
        )
    ]
    return children


if __name__ == '__main__':
    app.run_server(debug=True)
