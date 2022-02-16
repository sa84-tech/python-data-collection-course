import hashlib
import json
import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DB_URI = os.environ.get('DB_URI')
client = MongoClient(DB_URI)
collection = client.prom_bez['group-3-up-to-1000V']


result = list(collection.find({}, {'question_number': 1, 'question_text': 1, 'correct_answers': 1, '_id': 0}).sort('question_number', 1))

with open('answers.txt', 'w', encoding='utf-8') as f_n:
    for item in result:
        f_n.write(f"{item['question_number']}. {item['question_text']}\n  * {item['correct_answers'][0]}\n\n")


print('Done')

