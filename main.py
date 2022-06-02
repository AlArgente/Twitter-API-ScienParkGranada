import tweepy
import credentials

from listener import StreamListener
from classifier import Classifier
from utils_db import check_table_exists_or_create_it, db_connection, insert_data_on_table

def main():    
    # Connect to db
    mydb = db_connection()
    
    if mydb.is_connected():
        print('DB Connected')
        # Create table if doesnt exists
        TABLE_NAME = 'Twitter'
        TRACK_WORDS = ['#FelizJueves']
        check_table_exists_or_create_it(mydb, table_name=TABLE_NAME)
        mydb.close()
        # Load credentials
        auth = tweepy.OAuthHandler(credentials.API_KEY,
                                    credentials.API_SECRET_KEY)
        auth.set_access_token(credentials.ACCESS_TOKEN,
                              credentials.ACCESS_TOKEN_SECRET)
        # api = tweepy.API(auth)
        classifier = Classifier()
        my_listener = StreamListener(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     access_token=auth.access_token, access_token_secret=auth.access_token_secret, classifier=classifier)
        # my_listener = StreamListener(bearer_token=credentials.BEARER_TOKEN)
        # my_stream = tweepy.Stream(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     # access_token=auth.access_token, access_token_secret=auth.access_token_secret,
                                     # listener=my_listener)
        # result = my_listener.filter(languages=['es', 'en'], track=TRACK_WORDS)
        my_listener.filter(languages=['es', 'en'], track=TRACK_WORDS)

if __name__ == '__main__':
    main()