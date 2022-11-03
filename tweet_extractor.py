"""
File that use the Twitter API with an elevated account credentials to download tweets about some hashtags,
and store them in a SQLite3 database.

This file must be running on background to download tweets about the TRACK_WORDS.
"""
import os
import tweepy
import credentials_elevated as credentials

from listener import StreamListener
import tweetnlp
from utils_db import check_table_exists_or_create_it, db_connection, check_connection_db, \
    DB_NAME, TABLE_NAME, TRACK_WORDS


def main():
    # Create the database file if doesn't exists.
    if not os.path.exists('test.db'):
        open(DB_NAME, 'a').close()
    # Connect to db
    conn = db_connection()

    if check_connection_db(conn):
        print('DB Connected')
        # Load classification models
        classifier = tweetnlp.load('sentiment')  #  Using tweetnlp
        topic_classifier = tweetnlp.load('topic_classification')  #  Using tweetnlp
        # Create table if doesnt exists
        check_table_exists_or_create_it(conn, table_name=TABLE_NAME)
        conn.close()
        # Load credentials
        auth = tweepy.OAuthHandler(credentials.API_KEY,
                                   credentials.API_SECRET_KEY)
        auth.set_access_token(credentials.ACCESS_TOKEN,
                              credentials.ACCESS_TOKEN_SECRET)
        # api = tweepy.API(auth)
        # Create a listener to download the tweets.
        my_listener = StreamListener(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     access_token=auth.access_token, access_token_secret=auth.access_token_secret,
                                     classifier=classifier, topic_classifier=topic_classifier)
        print('Listening')
        my_listener.filter(languages=['es', 'en'], track=TRACK_WORDS)


if __name__ == '__main__':
    main()
