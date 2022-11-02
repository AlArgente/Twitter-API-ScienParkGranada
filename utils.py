# Document with some utils functions
import re
import json
from collections import Counter
from venv import create
import emoji
from matplotlib.pyplot import text
import pandas as pd
import unicodedata
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
    new_datetime = datetime.strftime(datetime.strptime(dtime, '%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
    return datetime.strptime(new_datetime, '%Y-%m-%d %H:%M:%S')


def format_time_sql(time):
    time = str(time).split('T')
    return ' '.join(time)


def format_new_time(time_str):
    new_time = re.split('T|\.', time_str)
    new_time = new_time[:2]
    new_time = ' '.join(new_time)
    return datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')


def month_str_to_int(month):
    """Function to convert the month as letters to numbers.

    Args:
        month (str): Month as letters

    Returns:
        str: Month as numbers.
    """
    MONTHS = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
              'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
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
    new_text = ' '.join(
        [word if word not in df['Bytes'] else str(df.loc[df['Bytes'] == word]['Des_spanish']) for word in new_text])
    print(f"Text after removing emojis: {new_text}")
    return new_text


def remove_emoji_from_text(text):
    """Function to remove emojis from the text.

    Args:
        text (str): Tweet to be cleaned.

    Returns:
        str: Tweets without emojis.
    """
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


def get_tweets_by_hashtag(api, clf, topic_clf=None, hashtag="#FelizMartes", max_tweets=100, max_limit=100):
    """Function to get the tweets from a hashtag

    Args:
        api (Tweepy.API): Connection to the Twitter API
        clf (Classifier): The classifier selected to make the predictions.
        hashtag (str, optional): Hashtag to search Tweets from. Defaults to "#FelizMartes".
        max_tweets (int, optional): Max number of tweets to search in each call. Defaults to 100.
        max_limit (int, optional): Max number of tweets to search. Defaults to 1000.

    Returns:
        Pandas.DataFrame: DataFrame that contains the tweets, the user that created the tweet, the date and the polarity.
    """
    #  First method: Only get 100 tweets max
    #  tweets = list(api.search_tweets(q=hashtag, count=max_tweets, tweet_mode = "extended", exclude='retweets'))
    # Second method to get max_limit tweets from hashtag
    max_limit = min(max_tweets, max_limit)
    tweets_cursor = list(
        tweepy.Cursor(api.search_tweets, q=hashtag, count=100, tweet_mode="extended", exclude="retweets").items(
            max_limit))
    filtered_tweets = []
    usernames_tweets = []
    created_at_tweets = []
    polarity_tweets = []
    topic_tweets = []
    for tweet in tweets_cursor:
        clean_text = clean_tweet(decode_text(tweet.full_text))
        filtered_tweets.append(clean_text)
        #  polarity_tweets.append(clf.get_sentiment(clean_text)) # Using huggingface, works
        polarity_tweets.append(clf.sentiment(clean_text)['label'])  #  Using tweetnlp
        #  topic = topic_clf.get_topic(clean_text) # Using huggingface, works
        topic = topic_clf.topic(clean_text)['label']  #  Using tweetnlp
        topic = ', '.join(topic) if len(topic) else "No topic detected."
        #  print(f"Topic: {topic_clf.get_topic(clean_text)[0]}")
        topic_tweets.append(topic)
        usernames_tweets.append(tweet.user.screen_name)
        created_at = tweet.created_at
        created_at = created_at.astimezone(pytz.timezone('Europe/Madrid')).strftime('%Y-%m-%d %H:%M:%S')
        created_at_tweets.append(format_time_sql(created_at))
    users_info = {
        'text': filtered_tweets,
        'username': usernames_tweets,
        'created_at': created_at_tweets,
        'polarity': polarity_tweets,
        'topics': topic_tweets
    }
    return pd.DataFrame.from_dict(users_info)


def get_tweets_for_username(username, listener, clf, topic_clf=None, max_results=100, exclude='retweets',
                            max_limit=100):
    """Function that gets the tweets from a user. Max 100 tweets.

    Args:
        username (str): Username to search
        listener (ClientListener): Listener to search the tweets
        clf (Classifier): Model to make the predictions
        max_results (int, optional): Max number of tweets to retrieve. The upper limit is 100. Defaults to 100.
        exclude (str, optional): Option for the listener to add constrains to exclude tweets in the search. Defaults to 'retweets'.

    Returns:
        pd.DataFrame: A Pandas.DataFrame containing the tweets, polarity and when was the tweet created.
    """
    if max_results > 100:
        max_results = 100
    elif max_results <= 0:
        max_results = 20
    user_id = listener.get_user_id_by_username(username=username)
    user_tweets_response = tweepy.Paginator(listener.get_users_tweets, id=user_id, exclude=exclude,
                                            max_results=max_results, tweet_fields=['created_at']).flatten(
        limit=max_limit)
    user_tweets = []
    user_tweets_created_at = []
    for tweet in user_tweets_response:
        user_tweets.append(tweet.text)
        user_tweets_created_at.append(tweet.created_at)
    #  polarity = [clf.get_sentiment(tweet) for tweet in user_tweets] # Using transformers, works
    polarity = [clf.sentiment(tweet)['label'] for tweet in user_tweets]  #  Using tweetnlp, works
    #  topics = [topic_clf.get_topic(tweet) for tweet in user_tweets] # Using transofrmers, works
    topics = [', '.join(topic_clf.topic(tweet)['label']) for tweet in user_tweets]  #  Using tweetnlp, works
    data = {
        'text': user_tweets,
        'polarity': polarity,
        'created_at': user_tweets_created_at,
        'topics': topics
    }
    return pd.DataFrame.from_dict(data=data)


def get_most_frequent_words_from_tweets(df, clf):
    """Function that given a DataFrame gets the most frequents words. The text column must be named as 'text'.

    Args:
        df (Pandas.DataFrame): DataFrame containing the text.
        clf (Classifier): Classifier with which the prediction will be made

    Returns:
        Pandas.DataFrame: A DataFame containing the most used words.
    """
    content = ' '.join(df["text"])
    content = re.sub(r"http\S+", "", content)
    content = content.replace('RT ', ' ').replace('&amp;', 'and')
    content = re.sub('[^A-Za-z0-9]+', ' ', content)
    content = content.lower()
    stopwords_eng = stopwords.words('english')
    stopwords_spa = stopwords.words('spanish')
    text_tokenized = [word for word in word_tokenize(content) if
                      word not in stopwords_eng and word not in stopwords_spa]
    #  text_tokenized = [word for tweet in text for word in word_tokenize(tweet) if word not in stopwords_eng and word not in stopwords_spa]
    print(f"Text_token 0: {text_tokenized[0]}")
    fdist = FreqDist(text_tokenized)
    fd = pd.DataFrame(fdist.most_common(16), columns=["Word", "Frequency"]).drop([0]).reindex()
    #  fd['Polarity'] = fd['Word'].apply(lambda x: clf.get_sentiment(x)) # Using transformers
    fd['Polarity'] = fd['Word'].apply(lambda x: clf.sentiment(x)['label'])  #  Using tweetnlp
    fd['Marker_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 0.6)' if x == "Negative" else \
        ('rgba(184, 247, 212, 0.6)' if x == "Positive" else 'rgba(131, 90, 241, 0.6)'))
    fd['Line_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 1)' if x == "Negative" else \
        ('rgba(184, 247, 212, 1)' if x == "Positive" else 'rgba(131, 90, 241, 1)'))
    #  fd['Marker_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 0.6)' if x < -0.1 else \
    #      ('rgba(184, 247, 212, 0.6)' if x > 0.1 else 'rgba(131, 90, 241, 0.6)'))
    #  fd['Line_Color'] = fd['Polarity'].apply(lambda x: 'rgba(255, 50, 50, 1)' if x < -0.1 else \
    #      ('rgba(184, 247, 212, 1)' if x > 0.1 else 'rgba(131, 90, 241, 1)'))
    return fd


def get_num_pos_neg_neu_from_df(df):
    num_pos = df[df['polarity'] == "positive"]['polarity'].count()
    num_neg = df[df['polarity'] == "negative"]['polarity'].count()
    num_neu = df[df['polarity'] == "neutral"]['polarity'].count()
    return num_pos, num_neg, num_neu


def get_topics_count(df):
    return Counter(df['topics'])


def get_frequencies_from_text(text):
    text_tokenized_clean = get_text_clean(text)
    text_frequencies = {}
    for sentence in text_tokenized_clean:
        for word in sentence:
            if word in text_frequencies:
                text_frequencies[word] += 1
            else:
                text_frequencies[word] = 1
    return text_frequencies


def get_text_clean(text):
    stopwords_eng = stopwords.words('english')
    stopwords_eng += ['#', '"', ',', '.']
    stopwords_spa = stopwords.words('spanish')
    # text_tokenized_clean_joint = ' '.join([' '.join([word for word in word_tokenize(sentence) if word not in stopwords_eng and word not in stopwords_spa]) for sentence in text])
    return [[word for word in word_tokenize(clean_tweet(sentence)) if
             word not in stopwords_eng and word not in stopwords_spa] for sentence in text]


def get_text_joint(text):
    text_tokenized_clean = get_text_clean(text)
    return ' '.join([' '.join(list(sentence)) for sentence in text_tokenized_clean])
