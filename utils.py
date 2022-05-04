# Document with some utils functions
import re
import mysql
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

def db_connection(host='localhost', user='alberto', passwd='passwd', database='TwitterDB', charset='utf8'):
    return mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database,
        charset=charset
    )

def insert_data_on_table(mydb, data, table_name):
    print('Inserting data on db.')
    cursor = mydb.cursor()
    sql = f"INSERT INTO {table_name} (id_str, created_at, text, polarity,\
        user_created_at, user_location,\
            longitude, latitude, retweet_count, favorite_count) VALUES \
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (data['id_str'], data['created_at'], data['text'],\
                data['polarity'], data['user_created_at'], data['user_location'],\
                data['longitude'], data['latitude'], data['retweet_count'],\
                data['favorite_count'])
    cursor.execute(sql, val)
    mydb.commit()
    print('Data inserted on db.')
    cursor.close()
    
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