# Document with some utils functions
import re
import json
from venv import create
import emoji
from matplotlib.pyplot import text
import pandas as pd
import mysql.connector
import unicodedata
import time
import tweepy
from datetime import datetime
import pytz
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

TIMEZONE = pytz.timezone('Europe/Madrid')

def clean_tweet(tweet): 
    ''' 
    Use simple regex to clean tweet text by removing links and special characters
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                |(\w+:\/\/\S+)", " ", tweet).split()) 

def decode_text(text):
    """Function that transform the data from unidecode to ascii
        """
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                    if unicodedata.category(c) != 'Mn')
    
def format_time(dtime):
    """Function to formate time format from Twitter API to SQL time.
    
    SQL Time: '%Y-%m-%d %H:%M:%S'

    Args:
        time (string): string containing the time when tweet was published.
    """
    new_datetime = datetime.strftime(datetime.strptime(dtime,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
    aux_datetime = datetime.strptime(new_datetime,  '%Y-%m-%d %H:%M:%S')
    # time = time.split(' ')
    # day = time[2]
    # month = month_str_to_int(time[1])
    # year = time[5]
    # hour = time[3]
    # return f"{year}-{month}-{day} {hour}"
    return aux_datetime

def format_time_sql(time):
    time = str(time).split('T')
    return ' '.join(time)

def month_str_to_int(month):
    MONTHS = {'jan':'01', 'feb':'02', 'mar':'03', 'apr':'04', 'may':'05', 'jun':'06',
              'jul':'07', 'aug':'08', 'sep':'09', 'oct':'10', 'nov':'11', 'dec':'12'}
    return MONTHS[month.lower()]

def replace_emoji_from_text(df, text):
    """Function to replace the emojis for it's description.

    Args:
        df (Pandas.DataFrame): DataFrame with the emojis description.
        text (str): Tweet with emojis

    Returns:
        str: Tweet with the descriptiong of the emojis instead of the emojis.
    """
    print(f"Text before removing emojis: {text}")
    new_text = text.split(' ')
    new_text = ' '.join([word if word not in df['Bytes'] else str(df.loc[df['Bytes']==word]['Des_spanish']) for word in new_text])
    print(f"Text after removing emojis: {new_text}")
    return new_text

def remove_emoji_from_text(text):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", re.UNICODE)
    return re.sub(emoj, '', text)

def get_tweets_by_hashtag(api, clf, hashtag="#FelizMartes", max_tweets=100, max_limit=1000):
    # First method: Only get 100 tweets max
    tweets = list(api.search_tweets(q=hashtag, count=max_tweets, tweet_mode = "extended", exclude='retweets'))
    # Second method to get max_limit tweets from hashtag
    tweets_cursor = list(tweepy.Cursor(api.search_tweets, q=hashtag, count=100, tweet_mode="extended", exclude="retweets").items(max_limit))
    filtered_tweets = []
    usernames_tweets = []
    created_at_tweets = []
    polarity_tweets = []
    for tweet in tweets_cursor:
        clean_text = clean_tweet(decode_text(tweet.full_text))
        filtered_tweets.append(clean_text)
        polarity_tweets.append(clf.get_sentiment(clean_text))
        usernames_tweets.append(tweet.user.screen_name)
        created_at = tweet.created_at
        # created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        created_at = created_at.astimezone(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')
        created_at_tweets.append(format_time_sql(created_at))
    # print(f"Longitud de tweets leídos con cursor: {len(filtered_tweets)}")
    """
    filtered_tweets = []
    usernames_tweets = []
    created_at_tweets = []
    polarity_tweets = []
    for tweet_status in tweets:
        tweet = json.loads(json.dumps(tweet_status._json))
        if tweet.get('retweeted_status'):
            print('Avoiding retweets!')
            cnt += 1
        else:
            clean_text = clean_tweet(decode_text(tweet['full_text']))
            filtered_tweets.append(clean_text)
            polarity_tweets.append(clf.get_sentiment(clean_text))
            usernames_tweets.append(tweet['user']['screen_name'])
            created_at = format_time_sql(format_time(tweet['created_at']))
            created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            created_at = created_at.astimezone(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')
            created_at_tweets.append(format_time_sql(created_at))
    print(f"Longitud de tweets leídos sin paginator: {len(filtered_tweets)}")
    """
    users_info = {
        'text':filtered_tweets,
        'username':usernames_tweets,
        'created_at':created_at_tweets,
        'polarity': polarity_tweets
    }
    return pd.DataFrame.from_dict(users_info)

def get_tweets_for_username(username, listener, clf, max_results=100, exclude='retweets', max_limit=1000):
    """Function that gets the tweets from a user. Max 100 tweets.

    Args:
        username (str): Username to search
        listener (ClientListener): Listener to search the tweets
        clf (Classifier): Model to make the predictions
        max_results (int, optional): Max number of tweets to retrieve. The upper limit is 100. Defaults to 100.
        exclude (str, optional): Option for the listener to add constrains to exclude tweets in the search. Defaults to 'retweets'.

    Returns:
        _type_: _description_
    """
    if max_results > 100:
        max_results = 100
    elif max_results <= 0:
        max_results = 20
    user_id = listener.get_user_id_by_username(username=username)
    user_tweets_response = tweepy.Paginator(listener.get_users_tweets, id=user_id, exclude=exclude, max_results=max_results, tweet_fields=['created_at']).flatten(limit=max_limit)
    user_tweets = []
    user_tweets_created_at = []
    for tweet in user_tweets_response:
        user_tweets.append(tweet.text)
        user_tweets_created_at.append(tweet.created_at)
    polarity = [clf.get_sentiment(tweet) for tweet in user_tweets]
    data = {'text':user_tweets, 'polarity':polarity, 'created_at':user_tweets_created_at}
    return pd.DataFrame.from_dict(data=data)

def retrieve_info_from_paginator_response(response, clf):
    tweets_text = []
    tweets_created_at = []
    polarity = []
    for tweet in response:
        tweets_text.append(tweet.text)
        tweets_created_at.append(tweet.created_at)
        polarity.append(clf.get_sentiment(tweet.text))
    return {'text':tweets_text, 'polarity':polarity, 'created_at': tweets_created_at}

def get_most_frequent_words_from_tweets(df, clf):
    content = ' '.join(df["text"])
    content = re.sub(r"http\S+", "", content)
    content = content.replace('RT ', ' ').replace('&amp;', 'and')
    content = re.sub('[^A-Za-z0-9]+', ' ', content)
    content = content.lower()
    stopwords_eng = stopwords.words('english')
    stopwords_spa = stopwords.words('spanish')
    text_tokenized = [word for word in word_tokenize(content) if word not in stopwords_eng and word not in stopwords_spa]
    # text_tokenized = [word for tweet in text for word in word_tokenize(tweet) if word not in stopwords_eng and word not in stopwords_spa]
    print(f"Text_token 0: {text_tokenized[0]}")
    fdist = FreqDist(text_tokenized)
    fd = pd.DataFrame(fdist.most_common(16), columns = ["Word","Frequency"]).drop([0]).reindex()
    fd['Polarity'] = fd['Word'].apply(lambda x: clf.get_sentiment(x))
    fd['Marker_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 0.6)' if x < -0.1 else \
        ('rgba(184, 247, 212, 0.6)' if x > 0.1 else 'rgba(131, 90, 241, 0.6)'))
    fd['Line_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 1)' if x < -0.1 else \
        ('rgba(184, 247, 212, 1)' if x > 0.1 else 'rgba(131, 90, 241, 1)'))
    return fd