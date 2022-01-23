import hashlib
import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DB_URI = os.environ.get('DB_URI')
client = MongoClient(DB_URI)
users_col = client.insta_parser['researched_users']


def get_related_users(u_name, u_type):
    pipeline = [
        {'$match': {'username': u_name}},
        {'$lookup':
            {
                'from': 'related_users',
                'localField': u_type,
                'foreignField': '_id',
                'as': f'_{u_type}_full'
            }},
        {'$project':
            {
                '_id': 0,
                'user_id': 1,
                'username': 1,
                f'_{u_type}_full': 1,
                'followers_count': {'$size': '$followers'},
                'following_count': {'$size': '$following'}
            }}
    ]
    data = list(users_col.aggregate(pipeline))
    if data:
        return data[0]
    return None


user_types = ['', 'followers', 'following']
username = input('Type user name: ')
user_type_index = int(input(f'Type 1 to display followers or 2 to display followings of user {username}: '))
if user_type_index in [1, 2]:
    result = get_related_users(username, user_types[user_type_index])
    pprint(result)
