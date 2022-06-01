"""Functions to create the database, to create the tables and other possible functions on the database.
"""
import pandas as pd
import mysql.connector
from db_tables import TablesEnum

def db_connection(host='localhost', user='alberto', passwd='passwd', database='TwitterDB', charset='utf8mb4'):
    return mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database,
        charset=charset
    )

def insert_data_on_table(mydb, data, table_name):
    print('Inserting data on db.')
    cursor = mydb.cursor()
    sql = f"INSERT INTO {table_name} (id_str, created_at, text, polarity,\
        user_created_at, user_location, user_name, user_id, \
            longitude, latitude, retweet_count, favorite_count) VALUES \
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (data['id_str'], data['created_at'], data['text'],\
                data['polarity'], data['user_created_at'], data['user_location'],\
                data['user_name'], data['user_id'], data['longitude'], \
                data['latitude'], data['retweet_count'], data['favorite_count'])
    cursor.execute(sql, val)
    mydb.commit()
    print('Data inserted on db.')
    cursor.close()

def check_table_exists_or_create_it(mydb, table_name='Twitter'):
    """Function that check if a table exists on the database, and create
    it if it doesn't exists.

    Args:
        mydb (MySQL connector): Connection to the database.
        table_name (str, optional): Name of the table to check. Defaults to 'Twitter'.
    """
    mycursor = mydb.cursor()
    mycursor.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_name = '{0}'
                        """.format(table_name)
    )
    if mycursor.fetchone()[0] != 1:
        if table_name.upper() in TablesEnum.__members__.keys():
            table_attributes = TablesEnum[table_name.upper()].value
        else:
            raise ValueError(f"The table {table_name} can't be created. Try with: " + ', '.join([t.name for t in TablesEnum]))
        mycursor.execute("""CREATE TABLE {} ({})
                            """.format(table_name, table_attributes))
        mydb.commit()
        print("Table created.")
    mycursor.close()

def query_db(table_name='Twitter', table_attributes=None, **kwargs):
    """Function that retrieves all the elements from a SQL Table.

    Args:
        table_name (str, optional): Table where search the tweets. Defaults to 'Twitter'.
        table_attributes (list, optional): List of attributes to retrieve. Defaults to None.

    Raises:
        ValueError: If not table attributes given it raises an error.
        ConnectionError: If cannont connect to the database it raises and error.

    Returns:
        Pandas.DataFrame: Al the elements from the table_name.
    """
    if not table_attributes:
        raise ValueError("Give table attributes to extract.")
    dbcon = db_connection()
    if not dbcon:
        raise ConnectionError("Error connecting to the database.")
    attribute_query = ', '.join(list(table_attributes))
    query = f"SELECT {attribute_query} FROM {table_name} ORDER BY {table_attributes[-1]} DESC"
    return pd.read_sql(query, con=dbcon)

def query_db_last_minutes(table_name="Twitter", table_attributes=None, **kwargs):
    """Function that retrieves the elements from a table in the last minutes. The number of minutes must be given in kwargs

    Args:
        table_name (str, optional): Table where search the tweets. Defaults to "Twitter".
        table_attributes (list, optional): List of attributes to retrieve. Defaults to None.

    Raises:
        ValueError: If not table attributes given it raises an error.
        ConnectionError: If cannont connect to the database it raises an error.

    Returns:
        Pandas.DataFrame: DataFrame with elements in the table_name in the last minutes.
    """
    minutes = kwargs['minutes']
    if not table_attributes:
        raise ValueError("Give table attributes to extract.")
    dbcon = db_connection()
    if not dbcon:
        raise ConnectionError("Error connecting to the database.")
    attribute_query = ', '.join(list(table_attributes))
    query = f"SELECT {attribute_query} FROM {table_name} WHERE created_at > NOW() - INTERVAL {minutes} DAY ORDER BY {table_attributes[-1]} DESC"
    return pd.read_sql(query, con=dbcon)

def query_total_tweets(table_name="Twitter"):
    """Function to get the number of elements in a SQL table.

    Args:
        table_name (str, optional): Table to get the elements count. Defaults to "Twitter".

    Raises:
        ConnectionError: If cannot connect to DataBase, it raises an error.

    Returns:
        int: Returns the number of elements in the table.
    """
    dbcon = db_connection()
    if not dbcon:
        raise ConnectionError("Error connecting to the database.")
    query = f"SELECT COUNT(*) from {table_name}"
    return pd.read_sql(query, con=dbcon).iloc[0].values[0]