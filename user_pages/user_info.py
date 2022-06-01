from dash import dcc, html, Input, Output, callback

username = 'AlArgente'

layout_user = html.Div([
    html.H3('Monitorizando tweets de un usuario en tiempo real.'),
    dcc.Dropdown(
        {f'Page 4 - {i}': f'{i}' for i in ['New York City', 'Montreal', 'Los Angeles']},
        id='page-4-dropdown'
    ),
    html.Div(id='page-4-display-value'),
    dcc.Location(id='url_user', refresh=False),
    html.Br(),
    html.Div(id='user_info'),
    dcc.Link('Go to Hashtag Page', href='/hashtag_info')
])


@callback(
    Output('page-4-display-value', 'children'),
    Input('page-4-dropdown', 'value'))
def display_value(value):
    return f'You have selected {value}'

@callback(
    Output('user_info', 'children'),
    Input('url_user', 'username'))
def username_info(username):
    return f"Username: {username}"
