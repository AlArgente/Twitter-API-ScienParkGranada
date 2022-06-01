import pandas as pd
import datetime
from dash import html, dash_table, dcc
from matplotlib import use
import plotly.graph_objs as go

from textblob import TextBlob

from utils import format_time_sql, get_tweets_by_hashtag, get_most_frequent_words_from_tweets
from utils_db import query_db_last_minutes, query_db

def generate_table_sql():
    df = query_db(table_attributes=['text', 'user_name', 'created_at'])
    return generate_table_from_df(df)

def generate_table(): # TODO: Cambiar nombre a generate_table_hashtag_sql
    df = query_db(table_attributes=['text', 'user_name', 'created_at'])
    df['created_at'] = df['created_at'].apply(lambda x: format_time_sql(x))
    df_columns = list(df.columns)
    table_column_names = ['Tweet', "Usuario", "Fecha publicación"]
    return dash_table.DataTable(
        columns=[{"name": f"{table_column_names[i]}", "id": df_columns[i]} for i in range(len(df_columns))],
        data=df.to_dict('records'),
        style_table={'height': '400px', 'overflowY': 'scroll'},
        # fixed_rows={'headers': True},
        style_cell={'minWidth': 15, 'width': 35, 'maxWidth': 1005, 'text-align': 'center'},
        style_cell_conditional=[
            {
                'if':{'column_id':'text'},
                'textAlign': 'left'
            },
            {
                'if':{'column_id':'text'},
                'textAlign': 'left'
            }
        ],
        style_header_conditional=[
            {
                'if':{'column_id':col},
                'fontWeight': 'bold'
            } for col in df_columns 
        ],
        style_header={'text-align': 'center'},
        style_data_conditional=[
            {
                'if':{'column_id':'text'},
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ],
        page_size=10,
        page_action='none'
    )

def generate_table_from_df(df):
    df_columns = list(df.columns)
    table_column_names = ['Tweet', "Usuario", "Fecha publicación"]
    return dash_table.DataTable(
        columns=[{"name": f"{table_column_names[i]}", "id": df_columns[i]} for i in range(len(df_columns))],
        data=df.to_dict('records'),
        style_table={'height': '400px', 'overflowY': 'scroll'},
        # fixed_rows={'headers': True},
        style_cell={'minWidth': 15, 'width': 35, 'maxWidth': 1005, 'text-align': 'center'},
        style_cell_conditional=[
            {
                'if':{'column_id':'text'},
                'textAlign': 'left'
            },
            {
                'if':{'column_id':'text'},
                'textAlign': 'left'
            }
        ],
        style_header_conditional=[
            {
                'if':{'column_id':col},
                'fontWeight': 'bold'
            } for col in df_columns 
        ],
        style_header={'text-align': 'center'},
        style_data_conditional=[
            {
                'if':{'column_id':'text'},
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ],
        page_size=10,
        page_action='none'
    )

def generate_timeline_user(username="DaSCI_es"):
    return html.Iframe(
                srcDoc=f'''
                    <a class="twitter-timeline" data-theme="light" href="https://twitter.com/{username}?ref_src=twsrc%5Etfw">
                        Tweets del usuario {username}.
                    </a>
                    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                ''',
                height=450,
                width=350
            )

def generate_pie_chart_from_df(df, username, days=10):
    """Function that generate a Pie Chart for Dash from a DataFrame given. The pie chart will show the % of tweets that are
    positive, negative and neutral.

    Args:
        df (pd.DataFrame): A Pandas DataFrame that contains the tweets and its labels.
        days (int, optional): Time period to see tweets from to today. Defaults to 10.
    
    Returns:
        Dash html.Div: A Dash html.Div that contains the Pie Chart, so it can be easily inserted into the Dash App.
    """
    num_pos, num_neg, num_neu = get_num_pos_neg_neu_from_df(df)
    return generate_pie_chart_less(num_pos=num_pos, num_neg=num_neg, num_neu=num_neu, username=username)

def generate_pie_char_tweets_user(username, listener, clf, max_results=100, exclude='retweets'):
    if max_results > 100:
        max_results = 100
    elif max_results <= 0:
        max_results = 20
    user_id = listener.get_user_id_by_username(username=username)
    user_tweets_response = listener.get_users_tweets(id=user_id, max_results=max_results, exclude=exclude)
    # print(f"Ya he leído los tweets de {username}")
    user_tweets = [tweet['text'] for tweet in user_tweets_response['data']]
    # print("Llego aquí!")
    polarity = [clf.get_sentiment(tweet) for tweet in user_tweets]
    data = {'text':user_tweets, 'polarity':polarity}
    # polarity = [TextBlob.polarity(tweet).sentiment for tweet in user_tweets]
    # print(f"Ya tengo la polaridad de los tweets de {username}")
    # df_user = pd.DataFrame([user_tweets, polarity], columns=['text', 'polarity'])
    df_user = pd.DataFrame.from_dict(data=data)
    # print(f"Ya he creado el DataFrame: {df_user}")
    num_pos, num_neg, num_neu = get_num_pos_neg_neu_from_df(df_user)
    # print(f"Positivos: {num_pos}. Negativos: {num_neg}. Neutros: {num_neu}.")
    return generate_pie_chart_less(num_pos=num_pos, num_neg=num_neg, num_neu=num_neu, username=username)

def get_num_pos_neg_neu_from_df(df):
    num_pos = df[df['polarity']==1]['polarity'].count()
    num_neg = df[df['polarity']==-1]['polarity'].count()
    num_neu = df[df['polarity']==0]['polarity'].count()
    return num_pos, num_neg, num_neu

def generate_pie_chart(table_name='Twitter', table_attributes=None, days=10):
    """Function that generate a Dash Pie Chart for a given table_name and it's attributes for the last days selected
    or for the full time period.

    Args:
        table_name (str, optional): Name of the SQL table. Defaults to 'Twitter'.
        table_attributes (list, optional): List of table attributes to retrieve. Defaults to None.
        days (int, optional): Last days to select. Also can be str. If str then full time period will be applied. Defaults to 10.

    Returns:
        Dash html.Div: A Dash html.Div that contains the Pie Chart, so it can be easily inserted into the Dash App.
    """
    func = query_db if isinstance(days, str) else query_db_last_minutes
    title_chart = "Numero de tweets con el hashtag #..." if isinstance(days, str) else f"Número de tweets en los últimos {days} días."
    kwargs = {'minutes':days}
    table_attributes= ['text', 'user_name', 'created_at', 'polarity'] if table_attributes is None else table_attributes
    df = func(table_name='Twitter', table_attributes=table_attributes, **kwargs)
    # num_pos = df[df['polarity']==1]['polarity'].count()
    # num_neg = df[df['polarity']==-1]['polarity'].count()
    # num_neu = df[df['polarity']==0]['polarity'].count()
    num_pos, num_neg, num_neu = get_num_pos_neg_neu_from_df(df)
    return html.Div([
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
                            'title':title_chart,
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
            ], style={'height':450, 'width': '27%', 'display': 'inline-block'})

def generate_pie_chart_less(num_pos, num_neg, num_neu, username=None):
    if username is None:
        username = 'usuario'
    total = num_neg+num_neu+num_pos
    return html.Div([
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
                            'title':f'Últimos {total} tweets de {username}.',
                            'annotations':[
                                dict(
                                    text='{}'.format(total),
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

def generate_table_for_hashtag(df):
    # Drop polarity to generate the table
    if 'polarity' in df.columns:
        df = df.drop(columns=['polarity'])
    return generate_table_from_df(df)

def generate_scatter_graph(df):
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x - datetime.timedelta(hours=-2))
    print(f"DF head: {df.head()}")
    print(f"DF type created_at[0]: {type(df.iloc[0]['created_at'])}")
    print(f"DF created_at[0]: {df.iloc[0]['created_at']}")
    result = df.groupby([pd.Grouper(key='created_at', freq='10s'), 'polarity']).count().unstack(fill_value=0).stack().reset_index()
    time_series = result["created_at"][result['polarity']==0].reset_index(drop=True)
    return html.Div([
        dcc.Graph(
            id='scatter-graph',
            figure={
                'data': [
                    go.Scatter(
                        x = time_series,
                        y = result[result['polarity']==0].reset_index(drop=True),
                        name='Neutros',
                        opacity=0.8,
                        mode='lines',
                        line=dict(width=0.5, color='rgb(131, 90, 241)'),
                        stackgroup='one' 
                    ),
                    go.Scatter(
                        x = time_series,
                        y = result[result['polarity']==-1].reset_index(drop=True),
                        name='Negativos',
                        opacity=0.8,
                        mode='lines',
                        line=dict(width=0.5, color='rgb(255, 50, 50)'),
                        stackgroup='two' 
                    ),
                    go.Scatter(
                        x = time_series,
                        y = result[result['polarity']==1].reset_index(drop=True),
                        name='Positivos',
                        opacity=0.8,
                        mode='lines',
                        line=dict(width=0.5, color='rgb(184, 247, 212)'),
                        stackgroup='three' 
                    )
                ]
            }
        )
    ], style={'width': '73%', 'display': 'inline-block', 'padding': '0 0 0 20'})
    # return "In process"

def generate_barplot_most_used_words(df, clf):
    fd = get_most_frequent_words_from_tweets(df, clf)
    return html.Div([
                    dcc.Graph(
                        id='x-time-series',
                        figure = {
                            'data':[
                                go.Bar(                          
                                    x=fd["Frequency"].loc[::-1],
                                    y=fd["Word"].loc[::-1], 
                                    name="Neutrals", 
                                    orientation='h',
                                    marker_color=fd['Marker_Color'].loc[::-1].to_list(),
                                    marker=dict(
                                        line=dict(
                                            color=fd['Line_Color'].loc[::-1].to_list(),
                                            width=1),
                                        ),
                                )
                            ],
                            'layout':{
                                'hovermode':"closest"
                            }
                        }        
                    )
                ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 0 0 20'})
    # return "In process"