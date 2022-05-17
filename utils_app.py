from dash import html, dash_table, dcc
from matplotlib import use
import plotly.graph_objs as go

from utils import format_time_sql
from utils_db import query_db_last_minutes, query_db


def generate_table():
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

def generate_pie_chart(table_name='Twitter', table_attributes=None, days=10):
    func = query_db if isinstance(days, str) else query_db_last_minutes
    title_chart = "Numero de tweets con el hashtag #..." if isinstance(days, str) else f"Número de tweets en los últimos {days} días."
    kwargs = {'minutes':days}
    table_attributes= ['text', 'user_name', 'created_at', 'polarity'] if table_attributes is None else table_attributes
    df = func(table_name='Twitter', table_attributes=table_attributes, **kwargs)
    num_pos = df[df['polarity']==1]['polarity'].count()
    num_neg = df[df['polarity']==-1]['polarity'].count()
    num_neu = df[df['polarity']==0]['polarity'].count()
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

def generate_pie_chart_less(num_pos, num_neg, num_neu):
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
                            'title':'Tuits en los últimos 10 días',
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
            ], style={'width': '27%', 'display': 'inline-block'})