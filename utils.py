# Document with some utils functions
import re
import emoji
import pandas as pd
import mysql.connector
import unicodedata


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
    
def format_time(time):
    """Function to formate time format from Twitter API to SQL time.
    
    SQL Time: '%Y-%m-%d %H:%M:%S'

    Args:
        time (string): string containing the time when tweet was published.
    """
    time = time.split(' ')
    day = time[2]
    month = month_str_to_int(time[1])
    year = time[5]
    hour = time[3]
    return f"{year}-{month}-{day} {hour}"

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

def remove_emoji_from_text(df, text):
    print(f"Text before removing emojis: {text}")
    allchars = list(text.decode('utf-8'))
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    new_text =  ' '.join([str for str in text.decode('utf-8').split() if all(i not in str for i in emoji_list)])
    print(f"Text after removing emojis: {new_text}")
    return new_text