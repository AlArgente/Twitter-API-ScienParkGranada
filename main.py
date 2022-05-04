import tweepy
import credentials

from listener import StreamListener
from utils import db_connection, insert_data_on_table

def main():    
    # Connect to db
    mydb = db_connection()
    
    if mydb.is_connected():
        print('DB Connected')
        # Create table if doesnt exists
        TABLE_NAME = 'Twitter'
        TRACK_WORDS = ['ibai', 'vayne']
        mycursor = mydb.cursor()
        mycursor.execute("""
                         SELECT COUNT(*)
                         FROM information_schema.tables
                         WHERE table_name = '{0}'
                         """.format(TABLE_NAME)
        )
        if mycursor.fetchone()[0] != 1:
            TABLE_ATTRIBUTES = "id_str VARCHAR(255), created_at DATETIME, text VARCHAR(1025), \
            polarity INT, user_created_at VARCHAR(255), user_location VARCHAR(255), \
            user_name VARCHAR(255), longitude DOUBLE, latitude DOUBLE, \
            retweet_count INT, favorite_count INT"
            mycursor.execute("""CREATE TABLE {} ({})
                             """.format(TABLE_NAME, TABLE_ATTRIBUTES))
            mydb.commit()
            print("Database created.")
        mycursor.close()
        mydb.close()
        # Load credentials
        auth = tweepy.OAuthHandler(credentials.API_KEY,
                                    credentials.API_SECRET_KEY)
        auth.set_access_token(credentials.ACCESS_TOKEN,
                              credentials.ACCESS_TOKEN_SECRET)
        # api = tweepy.API(auth)
        my_listener = StreamListener(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     access_token=auth.access_token, access_token_secret=auth.access_token_secret)
        # my_listener = StreamListener(bearer_token=credentials.BEARER_TOKEN)
        # my_stream = tweepy.Stream(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     # access_token=auth.access_token, access_token_secret=auth.access_token_secret,
                                     # listener=my_listener)
        # result = my_listener.filter(languages=['es', 'en'], track=TRACK_WORDS)
        my_listener.filter(languages=['es', 'en'], track=TRACK_WORDS)
        # if result != -1:
        #     insert_data_on_table(mydb=mydb, data=result, table_name=TABLE_NAME)

if __name__ == '__main__':
    main()