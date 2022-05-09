import dash

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Real-Time Twitter Monitor'
# TODO: Define layouts and callbacks
# server = app.server
# app.run_server() # To run the server