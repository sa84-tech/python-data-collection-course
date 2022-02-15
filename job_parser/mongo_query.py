import hashlib
import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DB_URI = os.environ.get('DB_URI')
client = MongoClient(DB_URI)
collection = client.prom_bez['group-3-up-to-1000V']

while True:
    text = input('Question text: ')
    if text == 'exit':
        break
    result = list(collection.find({'question_text': {'$regex': f'.*{text}*.'}}))
    pprint(result)
