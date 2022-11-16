"""Functions to create the database, to create the tables and other possible functions on the database.
"""
import sqlite3
import pandas as pd
import mysql.connector

from enum import Enum

DB_NAME = "./test.db"
TABLE_NAME = 'Twitter'
TRACK_WORDS = ['#SentIA', '#ExpoIA']


class TablesEnum(Enum):
    TWITTER = "id INTEGER PRIMARY KEY AUTOINCREMENT, id_str VARCHAR(255), created_at DATETIME, text VARCHAR(1025), \
        polarity VARCHAR(255), topic VARCHAR(255), user_name VARCHAR(255), user_id VARCHAR(255)"


def db_connection():
    """
    Function that create a connection to a sqlit3 database
    Returns: Object with the connection to the database.

    """
    return sqlite3.connect(DB_NAME)


def check_connection_db(conn):
    """Function that check if a sqlite3 connection is on

    Args:
        conn (sqlite3.connection): Connection with a sqlite3 databse.

    Returns:
        bool: True/False if can create a cursor to the database.
    """
    try:
        conn.cursor()
        return True
    except Exception:
        return False


def db_connection_sql(host='localhost', user='alberto', passwd='passwd', database='TwitterDB', charset='utf8mb4'):
    return mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database,
        charset=charset
    )


def insert_data_on_table(conn, data, table_name):
    """Function that insert data into a table from a sqlite3 databse.
    The database must exits.

    Args:
        conn (sqlite3.connection): Connection with the sqlite3 database
        data (json): Data to insert
        table_name (str): Table name
    """
    curr = conn.cursor()
    sql = f"INSERT INTO {table_name} (id_str, created_at, text, polarity, topic,\
            user_name, user_id) VALUES \
            (?, ?, ?, ?, ?, ?, ?)"
    val = (data['id_str'], data['created_at'], data['text'],
           data['polarity'], data['topic'], data['user_name'],
           data['user_id'])
    curr.execute(sql, val)
    conn.commit()
    curr.close()


def check_table_exists_or_create_it(mydb, table_name='Twitter'):
    """Function that check if a table exists on the database, and create
    it if it doesn't exists.

    Args:
        mydb (MySQL connector): Connection to the database.
        table_name (str, optional): Name of the table to check. Defaults to 'Twitter'.
    """
    cursor = mydb.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        print("Table exists.")
    except sqlite3.OperationalError as e:
        if table_name.upper() in TablesEnum.__members__.keys():
            table_attributes = TablesEnum[table_name.upper()].value
        else:
            raise ValueError(
                f"The table {table_name} can't be created. Try with: " + ', '.join([t.name for t in TablesEnum])) from e

        cursor.execute(f'CREATE TABLE {table_name} ({table_attributes})')
        mydb.commit()
        print("Table created.")
    cursor.close()


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
    query = f"SELECT {attribute_query} FROM {table_name} DESC LIMIT 100"
    # We take 100, don't need to show more as people won't interact with it.
    # query = f"SELECT {attribute_query} FROM {table_name}"
    return pd.read_sql(query, con=dbcon)


def query_db_last_days(table_name="Twitter", table_attributes=None, **kwargs):
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
    days = kwargs['days']
    if not table_attributes:
        raise ValueError("Give table attributes to extract.")
    dbcon = db_connection()
    if not dbcon:
        raise ConnectionError("Error connecting to the database.")
    attribute_query = ', '.join(list(table_attributes))
    #  query = f"SELECT {attribute_query} FROM {table_name} WHERE created_at > NOW() - INTERVAL {minutes} DAY ORDER BY {table_attributes[-1]} DESC" # Works for SQL
    # query = f"SELECT {attribute_query} FROM {table_name} WHERE created_at BETWEEN datetime('now') and strftime({minutes})"  #  For SQLite3
    # For asuming we do not exceed the RAM limit, we set a 10ks limit for the tweets
    query = f"SELECT {attribute_query} FROM {table_name} WHERE created_at BETWEEN datetime('now', '-{days} days') and datetime('now') LIMIT 10000"
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


def query_num_pos_neg_neu_from_db(table_name='Twitter'):
    """
    Function to query the number of positives, negatives and neutral tweets from the database
    Args:
        table_name:

    Returns:

    """
    dbcon = db_connection()
    if not dbcon:
        raise ConnectionError("Error connecting to the database.")
    query_num_pos = "WHERE polarity='Positivo'"
    query_num_neg = "WHERE polarity='Negativo'"
    query_num_neu = "WHERE polarity='Neutro'"
    curr = dbcon.cursor()
    num_pos = query_count_from_db(curr=curr, constraints=query_num_pos)
    num_neg = query_count_from_db(curr=curr, constraints=query_num_neg)
    num_neu = query_count_from_db(curr=curr, constraints=query_num_neu)
    curr.close()
    dbcon.close()
    return num_pos, num_neg, num_neu


def query_count_from_db(dbcon=None, curr=None, table_name='Twitter', constraints=''):
    if dbcon is None and curr is None:
        dbcon = db_connection()
        if not dbcon:
            raise ConnectionError("Error connecting to the database.")
    if dbcon and curr is None:
        curr = dbcon.cursor()
    query = f"SELECT count(*) from {table_name} {constraints}"
    return curr.execute(query).fetchone()[0]
