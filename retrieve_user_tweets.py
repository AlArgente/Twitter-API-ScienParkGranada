import os
import tweepy
import credentials
import argparse
import time
import pandas as pd
# from classifier import Classifier
from client_listener import ClientListener


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, help="User to search tweets from", default='DaSCI_es')
    args = vars(parser.parse_args())
    username = args['username']
    # Authentication
    auth = tweepy.OAuthHandler(credentials.API_KEY,
                            credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN,
                            credentials.ACCESS_TOKEN_SECRET)
    # classifier = Classifier()
    # API to search tweets instead of listener?
    # api = tweepy.API(auth)
    client_listener = ClientListener(bearer_token=credentials.BEARER_TOKEN, consumer_key=auth.consumer_key,
                                     consumer_secret=auth.consumer_secret, access_token=auth.access_token,
                                     access_token_secret=auth.access_token_secret) # , return_type=dict)
    #######
    # Output file_name #
    output_path = f"users_tweets/{username}.csv"
    #######
    user_id = client_listener.get_user_id_by_username(username=username)
    print(f"User ID: {user_id}")
    tweet_fields = ['created_at', 'geo', 'author_id', 'context_annotations', 'conversation_id', 'entities',
                    'attachments', 'in_reply_to_user_id', 'lang',
                    'possibly_sensitive', 'public_metrics', 'referenced_tweets', 
                    'reply_settings', 'source', 'withheld']
    all_tweet_fields = ['id', 'text'] + tweet_fields
    user_tweets_response = client_listener.get_users_tweets(id=user_id, max_results=100, exclude='retweets', 
                                                            tweet_fields=tweet_fields)
    # Get the last tweet to search tweets since
    data, last_tweet_id = retrieve_info_tweets(user_tweets_response, all_tweet_fields)
    all_data = {key: [] for key in all_tweet_fields}
    all_data = extend_data_info(all_data=all_data, new_data=data, tweet_fields=all_tweet_fields)
    #######
    # CSV FILE #
    save_data_to_csv(all_data, output_path)
    #######
    while True:
        user_tweets_response = client_listener.get_users_tweets(id=user_id, max_results=100, since_id=last_tweet_id,
                                                                exclude='retweets', tweet_fields=tweet_fields)
        if user_tweets_response.meta['result_count'] != 0:
            data, last_tweet_id = retrieve_info_tweets(user_tweets_response, all_tweet_fields)
            print(f"Total tweets in this iteration: {len(data['text'])}")
            # all_data = extend_data_info(all_data=all_data, new_data=data, tweet_fields=all_tweet_fields)
            save_data_to_csv(data, output_path)
        else:
            # Wait 2 hours until next try
            print("No new tweets yet. Waiting 2 hours until next try.")
            time.sleep(7200)

def retrieve_info_tweets(response, tweet_fields):
    last_tweet_id = response.meta['newest_id']
    data = {key: [] for key in tweet_fields}
    for tweet in response.data:
        tweet = dict(tweet)
        for field in tweet_fields:
            data[field].append(tweet.get(field, 'Missing'))
    return data, last_tweet_id

def extend_data_info(all_data, new_data, tweet_fields):
    for field in tweet_fields:
        all_data[field].extend(new_data[field])
    return all_data

def save_data_to_csv(data, output_path):
    df = pd.DataFrame.from_dict(data)
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index_label=False, index=False)

if __name__ == '__main__':
    main()