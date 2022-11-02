import os
import re
import json
import pandas as pd
import tweepy
from textblob import TextBlob

import mysql.connector
from utils import clean_tweet, decode_text, format_time, remove_emoji_from_text, format_new_time
from utils_db import db_connection, insert_data_on_table

# tweepy.asynchronous.AsyncStream

class StreamListenerAnd(tweepy.StreamingClient):
    # class StreamListenerAnd(tweepy.Stream):
    # class StreamListener(tweepy.asynchronous.AsyncStream):
    """Class to get tweets
    
    """
    
    def __init__(self, bearer_token, *, return_type=..., wait_on_rate_limit=True, 
                 output_path, **kwargs):
        super().__init__(bearer_token, return_type=return_type, wait_on_rate_limit=wait_on_rate_limit, **kwargs)
        self.__output_path = output_path
    
    # def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, 
    #              output_path, **kwargs):
    #     super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, **kwargs)
    #     self.__df_emojis = pd.read_csv('descriptions_of_emojis.csv', sep=';')
    #     self.__output_path = output_path

    def on_connect(self):
        return super().on_connect()

    def on_connection_error(self):
        print("Error de conexión")

    def on_data(self, status):
        # Here we have to extract info about the tweets
        status = json.loads(status)
        print(status.keys())
        status = status['data']
        # if 'retweeted_status' in status.keys() or 
        if 'referenced_tweets' in status.keys() and status['referenced_tweets'][0]['type'] == 'retweeted':
            # Avoid retweets
            return True
        # if status['truncated']:
        #     text = str(clean_tweet(decode_text(status['extended_tweet']['full_text'])))
        # else:
        print(status.keys())
        print(status)
        text = str(clean_tweet(decode_text(status['text'])))
        # print(f"User keys: {status['user'].keys()}")
        id_str = status['id']
        print(type(status['created_at']))
        created_at = format_new_time(status['created_at'])
        user_location = remove_emoji_from_text(decode_text(status['user']['location'])) if status['user']['location'] is not None else 'Not specified'
        user_created_at = format_time(status['user']['created_at'])
        user_name = status['user']['username']
        user_id = status['user']['id']
        longitude = 0.0
        latitude = 0.0
        if status['geo']:
            longitude = status['coordinates']['coordinates'][0]
            latitude = status['coordinates']['coordinates'][1]

        retweet_count = status['retweet_count']
        favorite_count = status['favorite_count']

        data_to_store = {
            'id_str':[id_str], 'created_at':[created_at], 'text':[text],'user_id':[user_id],
            'user_location':[user_location], 'user_created_at':[user_created_at], 'user_name':[user_name],
            'longitude':[longitude], 'latitude':[latitude], 'retweet_count':[retweet_count], 'favorite_count':[favorite_count]
        }

        # Store data into msql
        self.__add_data_to_db(data=data_to_store)

    def on_request_error(self, status_code):
        """Function to take care of Twitter API rate limits.
        """
        if status_code == 420:
            # Disconnect from the stream
            return False

    def __add_data_to_db(self, data):
        try:
            df = pd.DataFrame.from_dict(data)
        except ValueError as er:
            print(data)
            print(f"Error: {er}")
        df.to_csv(self.__output_path, mode='a', header=not os.path.exists(self.__output_path), index_label=False, index=False)
        print('Data inserted')