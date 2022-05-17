import json
import pandas as pd
import tweepy
from tweepy import Client
from textblob import TextBlob

import mysql.connector
from utils import clean_tweet, decode_text, format_time, remove_emoji_from_text
from utils_db import db_connection, insert_data_on_table

class ClientListener(Client):
    def __init__(self, bearer_token=None, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None, *, return_type=..., wait_on_rate_limit=False):
        super().__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=return_type, wait_on_rate_limit=wait_on_rate_limit)

    def get_user_id_by_username(self, username=None):
        user_info = self.get_user(username=username)
        return user_info['data']['id']