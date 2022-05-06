"""Function to have possible tables and their attributes
"""

from enum import Enum


class TablesEnum(Enum):
    TWITTER = "id INT NOT NULL AUTO_INCREMENT, id_str VARCHAR(255), created_at DATETIME, text VARCHAR(1025), \
        polarity INT, user_created_at VARCHAR(255), user_location VARCHAR(255), \
        user_name VARCHAR(255), user_id VARCHAR(255), longitude DOUBLE, latitude DOUBLE, \
        retweet_count INT, favorite_count INT, PRIMARY KEY (id)"