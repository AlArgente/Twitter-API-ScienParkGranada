import pandas as pd

from utils_db import db_connection

def main():
    TABLE_NAME = "Twitter"
    TRACK_WORD = "#SVGala3"
    mydb = db_connection()
    query = "SELECT id_str, text, polarity, user_location, created_at FROM \
        {}".format(TABLE_NAME)
    df = pd.read_sql(query, con=mydb)
    print(f"Columns dataframe: {df.columns}")
    print(df.head())
    df['created_at'] = pd.to_datetime(df['created_at'])
    result = df.groupby(
        [pd.Grouper(key='created_at', freq='2s'), 'polarity']
    ).count().unstack(fill_value=0).stack().reset_index()
    result = result.rename(columns={'id_str': f"Num of '{TRACK_WORD}' mentions"})
    
    print(f"Result: {result}")

if __name__ == '__main__':
    main()