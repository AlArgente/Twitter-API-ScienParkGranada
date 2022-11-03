import dash
from dash import html, dcc
from dash.dependencies import State
import dash_bootstrap_components as dbc

from dash_extensions.enrich import DashProxy, MultiplexerTransform
from dash_extensions.enrich import Output as OutputExt
from dash_extensions.enrich import Input as InputExt

import tweepy
import credentials

from client_listener import ClientListener
import tweetnlp

from utils_app import generate_table_for_hashtag, generate_pie_chart_from_df, \
    generate_barplot_most_used_words, generate_timeline_user, generate_pie_chart_less, \
    generate_topics_pie_chart_from_df, generate_wordcloud
from utils import get_tweets_by_hashtag, get_tweets_for_username, get_num_pos_neg_neu_from_df


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
bootstrap_theme = [dbc.themes.BOOTSTRAP]
darkly = [dbc.themes.DARKLY]
cosmo = [dbc.themes.COSMO]
cyborg = [dbc.themes.CYBORG]
solar = [dbc.themes.SOLAR]
# app = dash.Dash(__name__) # , external_stylesheets=solar)
app = DashProxy(__name__, prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()])  #  , external_stylesheets=solar)
app.config.external_stylesheets = bootstrap_theme
app.title = 'Real-Time Twitter Monitor for users'

auth = tweepy.OAuthHandler(credentials.API_KEY,
                           credentials.API_SECRET_KEY)
auth.set_access_token(credentials.ACCESS_TOKEN,
                      credentials.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Sentiment analysis classifier
classifier = tweetnlp.load('sentiment')  #  Using tweetnlp
# Topic classifier
topic_classifier = tweetnlp.load('topic_classification')  #  Using tweetnlp
# ClientListener to retrieve the tweets.
client_listener = ClientListener(bearer_token=credentials.BEARER_TOKEN, consumer_key=auth.consumer_key,
                                 consumer_secret=auth.consumer_secret, access_token=auth.access_token,
                                 access_token_secret=auth.access_token_secret)

app.layout = html.Div([
    dcc.Input(id='input-1-state', type='text', value='DaSCI_es', placeholder="DaSCI_es"),
    html.Button(id='submit-button-state-user', n_clicks=0, children='Submit user'),
    dcc.Input(id='input-2-state', type='text', value='Hashtag'),
    html.Button(id='submit-button-state-hashtag', n_clicks=0, children='Submit hashtag'),
    html.Div(id='output-state'),
    html.Div(id='live-update-graph-appu'),
    #  Interval for refreshing the main page if user doesn't ask for anything.
    #  dcc.Interval(id='interval-component-slow',
    #               interval=300000, # 300000, # In miliseconds. 300000 = 5 minutes.
    #               n_intervals=0),
])


@app.callback(OutputExt('output-state', 'children'),
              InputExt('submit-button-state-user', 'n_clicks'),
              State('input-1-state', 'value'))
def update_output_with_username(n_clicks_user, input_user):
    return f'''
        The user button has the user value {input_user}.
    '''


@app.callback(OutputExt('output-state', 'children'),
              InputExt('submit-button-state-hashtag', 'n_clicks'),
              State('input-2-state', 'value'))
def update_output_with_hashtag(n_clicks_hashtag, input_hashtag):
    return f'''
        The hashtag button
        has the hashtah
        value {input_hashtag}.
    '''


@app.callback(OutputExt('live-update-graph-appu', 'children'),
              [  #  Input('interval-component-slow', 'n_intervals'),
                  InputExt('submit-button-state-user', 'n_clicks')],
              State('input-1-state', 'value'))
def update_graph_live_user(n, input_user):
    #  First load data and prepare data to show in the layout
    # Create the graph once data is loaded
    input_user = input_user if input_user[0] != '@' else input_user[1:]
    user_df = get_tweets_for_username(input_user, listener=client_listener, clf=classifier, topic_clf=topic_classifier,
                                      max_results=100)
    print(f"User df head: {user_df.head()}")
    children = [
        html.Div([
            generate_timeline_user("DaSCI_es"),
            generate_timeline_user("ParqueCiencias"),
            generate_timeline_user(input_user),
            generate_pie_chart_from_df(df=user_df, username=input_user),
            #  generate_scatter_graph(user_df),
            generate_barplot_most_used_words(user_df, clf=classifier, width=43),
            # html.Br(),
            generate_topics_pie_chart_from_df(user_df, width=43),
        ])
    ]
    return children


@app.callback(OutputExt('live-update-graph-appu', 'children'),
              [  #  Input('interval-component-slow', 'n_intervals'),
                  InputExt('submit-button-state-hashtag', 'n_clicks')],
              State('input-2-state', 'value'))
def update_graph_live_hashtag(n, input_hashtag):
    #  First load data and prepare data to show in the layout
    # data_from = "Twitter. Hashtag: #Eurovision, #FelizMiércoles"
    input_hashtag = input_hashtag if input_hashtag[0] == '#' else f"#{input_hashtag}"
    # Create the graph once data is loaded
    hashtag_df = get_tweets_by_hashtag(api, classifier, topic_classifier, input_hashtag, max_tweets=100)
    print(f"Hashtag df head:\n {hashtag_df.head()}")
    children = [
        html.Div([
            generate_table_for_hashtag(hashtag_df),  # Generate table
            html.Br(),
            generate_pie_chart_less(*get_num_pos_neg_neu_from_df(hashtag_df), username=input_hashtag),
            generate_barplot_most_used_words(hashtag_df, clf=classifier),
            generate_timeline_user("ParqueCiencias"),
            html.Br(),
            generate_topics_pie_chart_from_df(hashtag_df),
            html.Br(),
            generate_wordcloud(hashtag_df['text'].to_list()),
        ])
    ]
    return children


if __name__ == '__main__':
    app.run_server(debug=False)
