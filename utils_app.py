import pandas as pd
import numpy as np
import datetime
from dash import html, dash_table, dcc
import plotly.graph_objs as go

#  For wordcloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

from utils import format_time_sql, get_most_frequent_words_from_tweets, \
    get_topics_count, get_frequencies_from_text, get_num_pos_neg_neu_from_df
from utils_db import query_db_last_days, query_db, query_num_pos_neg_neu_from_db, query_count_from_db


def generate_table(emojis=None):
    """
    Function that create a DataTable with tweets and some info about them, such as the user that published the
    tweet, the date when it was published, and the polarity and topic for the tweet.

    This functions retrieve the data from the sqlite3 database.

    Returns (dash.DataTable): A table with the content

    """
    df = query_db(table_attributes=['text', 'user_name', 'created_at', 'polarity', 'topic'])
    # Format created_At column to strftime yyyy-mm-dd HH:MM:SS
    df['created_at'] = df['created_at'].apply(lambda x: format_time_sql(x))
    # Sort by date, latest tweets first
    df = df.sort_values(by="created_at", ascending=False)
    # Take only the day, not hour of publish
    df['created_at'] = df['created_at'].apply(lambda x: x.split(' ')[0])
    df_columns = list(df.columns)
    if emojis is not None:
        df['polarity'] = df['polarity'].apply(lambda x: f"{x}{emojis[x]}")
    # Add the table column names that will appear in the application. Manually change to add/delete columns.
    table_column_names = ['Tweet', "Usuario", "Fecha publicación", "Polaridad", "Topic"]
    return generate_table_from_df(df, df_columns=df_columns, table_column_names=table_column_names)


def generate_table_from_df(df, df_columns=None, table_column_names=None):
    """
    Function that generate a dash.DataTable given a pandas.DataFrame.
    Args:
        df(pandas.DataFrame): DataFrame with the data
        df_columns (list(str)): List with the columns of the DataFrame to show
        table_column_names (list(str)): List with the names of the columns to show in the table

    Returns dash_table.DataTble: DataTable with the given data.

    """
    if df_columns is None:
        df_columns = list(df.columns)
    # Add the table column names that will appear in the application. Manually change to add/delete columns.
    if table_column_names is None:
        table_column_names = ['Tweet', "Usuario", "Fecha publicación", "Polaridad", "Topic"]
    return dash_table.DataTable(
        columns=[{"name": f"{table_column_names[i]}", "id": df_columns[i]} for i in range(len(df_columns))],
        data=df.to_dict('records'),
        style_table={'height': '400px', 'overflowY': 'scroll', 'padding': '1em'},
        #  fixed_rows={'headers': True},
        style_cell={'minWidth': 15, 'width': 35, 'maxWidth': 1005, 'text-align': 'center'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'text'},
                'textAlign': 'left'
            },
            {
                'if': {'column_id': 'text'},
                'textAlign': 'left'
            }
        ],
        style_header_conditional=[
            {
                'if': {'column_id': col},
                'fontWeight': 'bold'
            } for col in df_columns
        ],
        style_header={'text-align': 'center', 'background_color':'#006825', 'color':'white'},
        style_data_conditional=[
            {
                'if': {'column_id': 'text'},
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ],
        page_size=10,
        page_action='none'
    )


def generate_timeline_user(username="DaSCI_es"):
    """
    Function that create an Iframe with the timeline about a given user.
    Args:
        username: Username to extract the timeline from

    Returns (html.Iframe): Iframe with the user's timeline.

    """
    return html.Iframe(
        srcDoc=f'''
                    <a class="twitter-timeline" data-theme="light" href="https://twitter.com/{username}?ref_src=twsrc%5Etfw">
                        Tweets del usuario {username}.
                    </a>
                    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                ''',
        height=425, # 450
        width=325 # 350
    )


def generate_wordcloud(text):
    """
    Function that creates a wordcloud given a DataFrame, and it uses an image as a mask and fill the Image with
    the given text.

    Args:
        text (Union[pd.Series, list]): All the text that will be used to fill the wordcloud.

    Returns (html.Center): A HTML component with the wordcloud image at the center of it.

    """
    # Posible masks to use
    #  mask = np.array(Image.open('img/SiluetaAlhambra.jpg'))
    # mask = np.array(Image.open('img/SiluetaAlhambra.png'))
    #  mask = np.array(Image.open('img/TwitterLogoPNGnbg.png'))
    # mask = np.array(Image.open('img/parquedelasciencias_nbg.png'))
    mask = np.array(Image.open('img/Parque-Ciencias-Granada-removebg-preview.png'))
    #  mask = np.array(Image.open('img/provincia-de-granada.jpg'))
    mask_colors = ImageColorGenerator(mask)
    text = get_frequencies_from_text(text)
    #  text = get_text_joint(df['text'])
    mask[mask == 0] = 255
    wc = WordCloud(width=mask.shape[1] * 5, height=mask.shape[0] * 5,
                # width = 500, height = 400,
                colormap='Set2', collocations=False,
                max_words=50000, background_color="white", mask=mask,
                color_func=mask_colors,  # words color
                contour_color='#023075', contour_width=1,  # Border color and size
                random_state=1, stopwords=STOPWORDS).generate_from_frequencies(text)
    wc.to_file('img_saves/img_transparent.png')
    return html.Center(html.Img(src=wc.to_image()))


def generate_pie_chart_from_df(df, username, days=10):
    """Function that generate a Pie Chart for Dash from a DataFrame given. The pie chart will show the % of tweets that are
    positive, negative and neutral.

    Args:
        username (str): Username.
        df (pd.DataFrame): A Pandas DataFrame that contains the tweets and its labels.
        days (int, optional): Time period to see tweets from to today. Defaults to 10.

    Returns:
        Dash html.Div: A Dash html.Div that contains the Pie Chart, so it can be easily inserted into the Dash App.
    """
    num_pos, num_neg, num_neu = get_num_pos_neg_neu_from_df(df)
    return generate_pie_chart_less(num_pos=num_pos, num_neg=num_neg, num_neu=num_neu, username=username)


def generate_pie_chart_from_db(username):
    num_pos, num_neg, num_neu = query_num_pos_neg_neu_from_db()
    return generate_pie_chart_less(num_pos, num_neg, num_neu, username)


def generate_pie_chart(table_name='Twitter', table_attributes=None, days=10, hashtag='Twitter'):
    """Function that generate a Dash Pie Chart for a given table_name and it's attributes for the last days selected
    or for the full time period.

    Args:
        table_name (str, optional): Name of the SQL table. Defaults to 'Twitter'.
        table_attributes (list, optional): List of table attributes to retrieve. Defaults to None.
        days (int, optional): Last days to select. Also can be str. If str then full time period will be applied. Defaults to 10.

    Returns:
        Dash html.Div: A Dash html.Div that contains the Pie Chart, so it can be easily inserted into the Dash App.
    """
    if isinstance(days, str):
        title_chart = f"Numero de tweets con el hashtag #{hashtag}"
        num_pos, num_neg, num_neu = query_num_pos_neg_neu_from_db()
    else:
        days_str = 'minutos'
        title_chart = f"Número de tweets en los últimos {days} {days_str}."
        days = int(days)
        days_str = 'minutes'
        num_pos = query_count_from_db(constraints=f"WHERE polarity='Positivo' AND created_at BETWEEN datetime("
                                                f"'now', '-{days} {days_str}') and datetime('now')")
        num_neg = query_count_from_db(constraints=f"WHERE polarity='Negativo' AND created_at BETWEEN datetime("
                                                f"'now', '-{days} {days_str}') and datetime('now')")
        num_neu = query_count_from_db(constraints=f"WHERE polarity='Neutro' AND created_at BETWEEN datetime("
                                                f"'now', '-{days} {days_str}') and datetime('now')")
    return generate_pie_chart_less(num_pos, num_neg, num_neu, username=hashtag, title=title_chart)


def generate_pie_chart_less(num_pos, num_neg, num_neu, username=None, title=None):
    if username is None:
        username = 'usuario'
    total = num_neg + num_neu + num_pos
    if title is None:
        title = f'Últimos {total} tweets de {username}.'
    return html.Div([
        dcc.Graph(
            id='pie-chart',
            figure={
                'data': [
                    go.Pie(
                        labels=['Positivos', 'Negativos', 'Neutros'],
                        values=[num_pos, num_neg, num_neu],
                        name='Polaridad',
                        marker_colors=['rgba(184, 247, 212, 0.6)', 'rgba(255, 50, 50, 0.6)', 'rgba(131, 90, 241, 0.6)'],
                        textinfo='value',
                        hole=.65
                    )
                ],
                'layout': {
                    'showLeyend': False,
                    'title': title,
                    'annotations': [
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
    ], style={'width': '25%', 'display': 'inline-block', 'position': 'relative'}) # 'width': '27%' in the old version


def generate_topics_pie_chart_from_df(df, width=69):
    topics_count = get_topics_count(df)
    return generate_topics_pie_chart(topics_count, width=width)


def generate_topics_pie_chart(topics_count, width=68):
    """Function tha recieves a df with the topics and the topic counts

    Args:
        topics_count (_type_): _description_
        width (int): width size for the pie chart.
    """
    total = sum(topics_count.values())
    return html.Div(
        html.Div([
            dcc.Graph(
                id='pie-chart-topics',
                figure={
                    'data': [
                        go.Pie(
                            labels=list(topics_count.keys()),
                            values=list(topics_count.values()),
                            name="Topics",
                            textinfo='value',
                            hole=.65
                        )
                    ],
                    'layout': {
                        'showLeyend': False,
                        'title': "Topics presentes en los tweets",
                        'annotations': [
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
        ], style={
            "width": "100%",
            "height": "100%",
        },  #  style={'width': '50%', 'display': 'inline-block', 'text-align':'center'}),
        ),
        style={
            "width": f"{width}%",
            "display": "inline-block",
            "padding-top": "5px",
            "padding-left": "1px",
            "overflow": "hidden"
        }
    )


def generate_table_for_hashtag(df):
    # Drop polarity to generate the table
    if 'polarity_' in df.columns:
        df = df.drop(columns=['polarity'])
    print(df)
    return generate_table_from_df(df)


def generate_scatter_graph(df):
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x - datetime.timedelta(hours=-2))
    print(f"DF head: {df.head()}")
    print(f"DF type created_at[0]: {type(df.iloc[0]['created_at'])}")
    print(f"DF created_at[0]: {df.iloc[0]['created_at']}")
    result = df.groupby([pd.Grouper(key='created_at', freq='10s'), 'polarity']).count().unstack(
        fill_value=0).stack().reset_index()
    time_series = result["created_at"][result['polarity'] == 0].reset_index(drop=True)
    return html.Div([
        dcc.Graph(
            id='scatter-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=time_series,
                        y=result[result['polarity'] == 0].reset_index(drop=True),
                        name='Neutros',
                        opacity=0.8,
                        mode='lines',
                        line=dict(width=0.5, color='rgb(131, 90, 241)'),
                        stackgroup='one'
                    ),
                    go.Scatter(
                        x=time_series,
                        y=result[result['polarity'] == -1].reset_index(drop=True),
                        name='Negativos',
                        opacity=0.8,
                        mode='lines',
                        line=dict(width=0.5, color='rgb(255, 50, 50)'),
                        stackgroup='two'
                    ),
                    go.Scatter(
                        x=time_series,
                        y=result[result['polarity'] == 1].reset_index(drop=True),
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
    #  return "In process"


def generate_barplot_most_used_words(df, clf, width=49):
    """
    Function that generate a bar plot with the most frequent words given a list of tweets.
    Args:
        df (pandas.DataFrame): DataFrame with the tweets
        clf (tweetnlp.Classifier): A sentiment analysis classifier
        width (int): Width for the bar plot. Default 49.

    Returns (html.Div): A html.Div with the generated bar plot.

    """
    fd = get_most_frequent_words_from_tweets(df, clf)
    return html.Div([
        dcc.Graph(
            id='x-time-series',
            figure={
                'data': [
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
                'layout': {
                    'hovermode': "closest"
                }
            }
        )
    ], style={'width': f"{width}%", 'display': 'inline-block', 'padding': '0 0 0 20'})


def background_dasci_img():
    src_img = 'img/logofullweb.png'
    img = Image.open(src_img)
    # img = img.resize((347, 43), Image.ADAPTIVE) # x(-20)
    # img = img.resize((261, 64), Image.ADAPTIVE) # x(-17)
    # img = img.resize((463, 57), Image.ADAPTIVE) # x(-15)
    img = img.resize((695, 86), Image.ADAPTIVE) # x(-10)
    return html.Img(src=img)
