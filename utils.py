# Document with some utils functions
import re
import emoji
import pandas as pd
import mysql.connector
import unicodedata
import time
from datetime import datetime

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