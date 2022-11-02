import json
import pandas as pd
import tweepy
from textblob import TextBlob

import mysql.connector
from utils import clean_tweet, decode_text, format_time, remove_emoji_from_text
from utils_db import db_connection, insert_data_on_table, check_connection_db


# tweepy.asynchronous.AsyncStream

class StreamListener(tweepy.Stream):
    # class StreamListener(tweepy.StreamingClient):
    # class StreamListener(tweepy.asynchronous.AsyncStream):
    """Class to get tweets
    """

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, classifier, topic_classifier,
                 **kwargs):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, **kwargs)
        self.__df_emojis = pd.read_csv('descriptions_of_emojis.csv', sep=';')
        self.__sentiment_task = classifier
        self.__topic_task = topic_classifier

    def on_connect(self):
        return super().on_connect()

    def on_connection_error(self):
        print("Error de conexión")

    def on_data(self, status):
        # Here we have to extract info about the tweets
        status = json.loads(status)
        if 'retweeted_status' in status.keys():
            # Avoid retweets
            return True
        if status['truncated']:
            text = str(clean_tweet(decode_text(status['extended_tweet']['full_text'])))
        else:
            text = str(clean_tweet(decode_text(status['text'])))
        #  print(f"User keys: {status['user'].keys()}")
        id_str = status['id_str']
        created_at = format_time(status['created_at'])
        #  sentiment = self.__sentiment_task.get_sentiment(text)
        sentiment = self.__sentiment_task.sentiment(text)['label']
        #  polarity = self.__polarity_str_to_int(sentiment)
        polarity = sentiment
        topic = ', '.join(list(self.__topic_task.topic(text)['label']))
        if not topic:
            topic = "Desconocido"
        #  topic = ', '.join(list(self.__topic_task.get_topic(text)))
        user_location = remove_emoji_from_text(decode_text(status['user']['location'])) if status['user'][
                                                                                               'location'] is not None else 'Not specified'
        user_created_at = format_time(status['user']['created_at'])
        user_name = status['user']['screen_name']
        user_id = status['user']['id_str']
        longitude = 0.0
        latitude = 0.0
        if status['coordinates']:
            longitude = status['coordinates']['coordinates'][0]
            latitude = status['coordinates']['coordinates'][1]

        retweet_count = status['retweet_count']
        favorite_count = status['favorite_count']

        data_to_store = {
            'id_str': id_str, 'created_at': created_at, 'text': text, 'sentiment': sentiment, 'user_id': user_id,
            'polarity': polarity, 'topic': topic, 'user_location': user_location, 'user_created_at': user_created_at,
            'user_name': user_name,
            'longitude': longitude, 'latitude': latitude, 'retweet_count': retweet_count,
            'favorite_count': favorite_count
        }

        # Store data into msql
        self.__add_data_to_db(data=data_to_store)

    def on_request_error(self, status_code):
        """Function to take care of Twitter API rate limits.
        """
        if status_code == 420:
            # Disconnect from the stream
            return False

    def on_exception(self, exception):
        print("EXCEPTION")
        return super().on_exception(exception)

    def on_request_error(self, status_code):
        print("Error 200 encontered while fetching tweets.")
        return super().on_request_error(status_code)

    def __add_data_to_db(self, data, table_name='Twitter'):
        conn = db_connection()
        if check_connection_db(conn):
            try:
                insert_data_on_table(conn=conn, data=data, table_name=table_name)
            except Exception as e:
                print(f"Exception encountered: {e}")
            conn.close()

    def __polarity_str_to_int(self, polarity):
        if polarity == 'Positive':
            return 1
        elif polarity == 'Negative':
            return -1
        else:
            return 0
