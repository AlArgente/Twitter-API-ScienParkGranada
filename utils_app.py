from dash import html, dash_table

def generate_table(df, max_rows=10):
    df_columns = list(df.columns)
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
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