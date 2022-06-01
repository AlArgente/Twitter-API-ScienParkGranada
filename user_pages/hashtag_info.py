from dash import dcc, html, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc

from utils_app import generate_table, generate_timeline_user, generate_pie_chart, generate_pie_chart_less
from utils_db import query_total_tweets


layout = html.Div(children=[
    html.H2('Monitorización de Twitter en tiempo real'),
    dcc.Interval(id='interval-component-slow',
                 interval=30000, # 300000, # In miliseconds. 300000 = 5 minutes.
                 n_intervals=0),
    # Here add more Divs to the layout
    html.Br(),
    html.Div(id='live-update-graph'),
    html.Div(id='live-update-bottom-graph'),
    html.Button('Submit hashtag: ', id='submit-hashtag', n_clicks=0),
    html.Button('Submit user: ', id='submit-user', n_clicks=0),
    html.Div(id='container-button-timestamp', children='Enter the user/hashtag to search:'),
    html.Div(id='page-3-display-value'),
    dcc.Link('Go to user page', href='/user_info'),
    html.Br(),
    dbc.Form(
        dbc.Row(
            [
                dbc.Label("User/Hashtag to search: ", width='auto'),
                dbc.Col(
                    dbc.Input(id='my-button', type="str", placeholder="Enter user/hashtag"),
                    class_name="me-3"
                ),
                dbc.Col(dbc.Button("Submit", color="primary"), width="auto"),
                html.Div(id='my-button-text'),
            ]
        )
    )
], className="dash-bootstrap")

@callback(Output('live-update-graph', 'children'),
              [Input('interval-component-slow', 'n_intervals')])
def update_graph_live(n):
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

@callback(
    Output('my-button-text', 'children'),
    Input('Submit', 'n_clicks'),
    State('my-button', 'value')
)
def update_output_div(n_clicks, value):
    return f"""You've entered "{value}" and clicked {n_clicks} times"""

@callback(
    # Output('container-button-timestamp', 'children'),
    Output('page-3-display-value', 'children'),
    Input('submit-hashtag', 'n_clicks'),
    Input('submit-user', 'n_clicks'),
    State('input-on-submit', 'value')
)
def redirect_output(n_clicks, value):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'submit-hashtag' in changed_id:
        return redirect_hashtag(value)
    elif 'submit-user' in changed_id:
        return redirect_user(value)
    else:
        return html.Div('Enter the user/hashtag to search.')

def redirect_hashtag(hashtag_to_search):
    return f'You have selected {hashtag_to_search}'

def redirect_user(user_to_search):
    return f'You have selected {user_to_search}'