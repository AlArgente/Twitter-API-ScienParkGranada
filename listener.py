import json
from os import stat
from turtle import st
import tweepy
from textblob import TextBlob

import credentials
from utils import clean_tweet, decode_text, db_connection, insert_data_on_table, format_time

# tweepy.asynchronous.AsyncStream

class StreamListener(tweepy.Stream):
# class StreamListener(tweepy.StreamingClient):
# class StreamListener(tweepy.asynchronous.AsyncStream):
    """Class to get tweets
    """

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, **kwargs):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, **kwargs)

    def on_data_new(self, raw_data):
        print(raw_data)
        raise ValueError('mimi')

    def on_connect(self):
        return super().on_connect()

    def on_connection_error(self):
        print("Error de conexión")

    def on_data(self, status):
        # Here we have to extract info about the tweets
        status = json.loads(status)
        text = clean_tweet(decode_text(status['text'])) # Preprocess text
        # if status['retweeted'] or text.startswith("RT "):
        if 'retweeted_status' in status.keys():
            # Avoid retweets
            print(f"RT avoided. Tweet: {text}")
            print(f"Tweet id: {status['id']}")
            print(f"User: {status['user']['screen_name']}")
            print(f"Tweet status retweeted: {status['retweeted_status']}")
            print(f"Tweet retweeted: {status['retweeted']}")
            print(f"Tamaño del tweet: {len(text)}")
            print(f"Tweet keys: {status.keys()}")
            print(f"Tweet truncated: {status['truncated']}")
            return True
        # Extract atributed from each tweet
        print('Normal tweet.')
        print(f"Tweet keys: {status.keys()}")
        # print(f"Display text range: {status['display_text_range']}")
        print(f"Len of tweet: {len(text)}")
        print(f"Tweet truncated: {status['truncated']}")
        if status['truncated']:
            print(f"Extended tweet not cleaned: {status['extended_tweet']}")
            extended_tweet = clean_tweet(decode_text(status['extended_tweet']['full_text']))
            print(f"Extended tweet: {extended_tweet}")
            print(f"Len of extended tweet: {len(extended_tweet)}")
        try:
            print(f"Tweet status retweeted: {status['retweeted_status']}")
        except KeyError as er:
            print("En los no retweets no hay retweeted_status.")
        print(f"User keys: {status['user'].keys()}")
        id_str = status['id_str']
        created_at = format_time(status['created_at'])
        # TODO: Add pipeline to extract sentiment with BERT Model, meanwhile I'm using textblob
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        user_location = decode_text(status['user']['location']) if status['user']['location'] is not None else 'Not specified'
        user_created_at = format_time(status['user']['created_at'])
        user_name = status['user']['name']

        longitude = 0.0
        latitude = 0.0
        if status['coordinates']:
            longitude = status['coordinates']['coordinates'][0]
            latitude = status['coordinates']['coordinates'][1]

        # print(text)
        # print(f"Long: {longitude}, Lati: {latitude}")

        retweet_count = status['retweet_count']
        favorite_count = status['favorite_count']
        
        data_to_store = {
            'id_str':id_str, 'created_at': created_at, 'text':text, 'sentiment':sentiment,
            'polarity': polarity, 'user_location':user_location, 'user_created_at':user_created_at, 'user_name':user_name,
            'longitude':longitude, 'latitude': latitude, 'retweet_count':retweet_count, 'favorite_count':favorite_count
        }
        
        # Store data into msql
        self.__add_data_to_db(data=data_to_store)

    def on_request_error(self, status_code):
        """Function to take care of Twitter API rate limits.
        """
        if status_code == 420:
            # Disconnect from the stream
            return False

    def __add_data_to_db(self, data, table_name='Twitter'):
        mydb = db_connection()
        if mydb.is_connected():
            insert_data_on_table(mydb=mydb, data=data, table_name=table_name)
            mydb.close()