"""Function to have possible tables and their attributes
"""

from enum import Enum


class TablesEnum(Enum):
    TWITTER = "id INTEGER PRIMARY KEY AUTOINCREMENT, id_str VARCHAR(255), created_at DATETIME, text VARCHAR(1025), \
        polarity VARCHAR(255), topic VARCHAR(255), user_created_at VARCHAR(255), user_location VARCHAR(255), \
        user_name VARCHAR(255), user_id VARCHAR(255), longitude DOUBLE, latitude DOUBLE, \
        retweet_count INT, favorite_count INT"