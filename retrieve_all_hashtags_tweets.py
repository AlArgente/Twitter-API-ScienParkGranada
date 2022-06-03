import os
import time

import tweepy
import credentials
import argparse

from listener_and import StreamListenerAnd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hashtag', type=str, help="Hashtag to search tweets from", default='#EleccionesAndalucia2022')
    args = vars(parser.parse_args())
    hashtag = args['hashtag']
    all_hashtags = ['#EleccionesAndalucia2022', '#AndalucíaAvanza', '#AndaluciaQuiereMas', '#SiVotamosGanamos',
                    '#PorAndalucia', '#CambioReal', '#AndalucíaLiberal']
    hashtag_save = 'all_hashtags'
    output_path = f"hashtags_tweets/{hashtag_save}.csv"
    auth = tweepy.OAuthHandler(credentials.API_KEY,
                                    credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN,
                            credentials.ACCESS_TOKEN_SECRET)
    
    my_listener = StreamListenerAnd(consumer_key=auth.consumer_key, consumer_secret=auth.consumer_secret,
                                     access_token=auth.access_token, access_token_secret=auth.access_token_secret,
                                     output_path=output_path)
    my_listener.filter(languages=['es'], track=all_hashtags)