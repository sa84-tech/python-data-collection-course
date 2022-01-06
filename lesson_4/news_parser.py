import os
import sys

import requests
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


LENTA_URL = 'https://lenta.ru/parts/news/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}

DB_URI = os.environ.get('DB_URI')
DB_NAME = os.environ.get('DB_NAME')

if not (DB_URI and DB_NAME):
    print('Add .env file with the variables DB_URI and DB_NAME.')
    sys.exit(1)

try:
    CLIENT = MongoClient(DB_URI)
    DB = CLIENT[DB_NAME]
except Exception as e:
    print('Error:', e)
    sys.exit(1)

NEWS_COLLECTION = DB.news
