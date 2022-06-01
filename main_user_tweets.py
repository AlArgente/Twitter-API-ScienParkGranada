import tweepy
import credentials

from classifier import Classifier
from client_listener import ClientListener


def main():
    auth = tweepy.OAuthHandler(credentials.API_KEY,
                            credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN,
                            credentials.ACCESS_TOKEN_SECRET)
    classifier = Classifier()
    client_listener = ClientListener(bearer_token=credentials.BEARER_TOKEN, consumer_key=auth.consumer_key,
                                     consumer_secret=auth.consumer_secret, access_token=auth.access_token,
                                     access_token_secret=auth.access_token_secret, return_type=dict)
    user_id = client_listener.get_user_id_by_username(username="zuhe18")
    print(f"User ID: {user_id}")
    user_tweets_response = client_listener.get_users_tweets(id=user_id, max_results=20, exclude='retweets')
    user_tweets = [tweet['text'] for tweet in user_tweets_response['data']]
    for tweet in user_tweets:
        print(f"Tweet: {tweet} has label: {classifier.get_sentiment(tweet)}")

if __name__ == '__main__':
    main()