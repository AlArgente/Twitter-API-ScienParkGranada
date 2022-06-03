import json
from multiprocessing.connection import wait
import os
import time

import tweepy
import credentials
import argparse

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, help="User to search tweets from", default='DaSCI_es')
    args = vars(parser.parse_args())
    username = args['username']
    # Authentication
    auth = tweepy.AppAuthHandler(credentials.API_KEY,
                            credentials.API_SECRET_KEY)
    # auth.set_access_token(credentials.ACCESS_TOKEN,
    #                         credentials.ACCESS_TOKEN_SECRET)
    auth.secure=True
    # classifier = Classifier()
    # API to search tweets instead of listener?
    api = tweepy.API(auth, retry_delay=300, wait_on_rate_limit=True) # , wait_on_rate_limit_notify=True)
    searchQuery = f'@{username}'
    retweet_filter='-filter:retweets'
    q=searchQuery+retweet_filter
    tweetsPerQry = 100
    output_file = f'mentions_users/{username}.csv'
    data = {}
    total_tweets_saved = 0
    while True:
        new_tweets = api.search_tweets(q=q, count=tweetsPerQry, exclude="retweets", tweet_mode="extended")
        if len(new_tweets)>0:
            for tweet in new_tweets:
                tweet = json.loads(json.dumps(tweet._json))
                for key, value in tweet.items():
                    data = save_data_factory(data=data, key=key, key_info=value)
            check_data_before_saving(data=data)
            total_tweets_saved += len(data)
            save_data_to_csv(data=data, output_path=output_file)
            # Wait 20 seconds if we retrieve more than 10ks tweets.
            if total_tweets_saved % 10000 == 0:
                time.sleep(20)
        else:
            wait_time = 120
            print(f"Waiting {wait_time} seconds for new possible tweets.")
            time.sleep(wait_time)

def save_user_info(data, user_info):
    if 'user' not in data:
        data['user'] = []
        data['user_id'] = []
        data['user_location'] = []
    data['user'].append(user_info['screen_name'])
    data['user_id'].append(user_info['id'])
    data['user_location'].append(user_info['location'])
    return data

def save_metadata_info(data, meta_info):
    if 'iso_language_code' not in data:
        data['iso_language_code'] = []
    data['iso_language_code'].append(meta_info['iso_language_code'])
    return data

def save_data_factory(data, key, key_info):
    if key == 'user':
        return save_user_info(data=data, user_info=key_info)
    elif key == 'metadata':
        return save_metadata_info(data=data, meta_info=key_info)
    elif key in ['extended_entities', 'possibly_sensitive', 'quoted_status_id', 'quoted_status_id_str', 'quoted_status']:
        return data
    else:
        if key not in data:
            data[key] = []
        data[key].append(key_info)
        return data

def check_data_before_saving(data):
    normal_lenght = 0
    for key, value in data.items():
        if len(value) != normal_lenght:
            print(f"El atributo {key} tiene una longitud de {len(value)}, que es diferente de {normal_lenght}.")
            normal_lenght = len(value)

def save_data_to_csv(data, output_path):
    df = pd.DataFrame.from_dict(data)
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index_label=False, index=False)


if __name__ == '__main__':
    main()