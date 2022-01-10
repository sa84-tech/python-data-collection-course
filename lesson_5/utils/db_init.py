import os
import sys

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_URI = os.environ.get('DB_URI')
DB_NAME = os.environ.get('DB_NAME')

if not (DB_URI and DB_NAME):
    print('Add .env file from the template file')
    sys.exit(1)

try:
    CLIENT = MongoClient(DB_URI)
    DB = CLIENT[DB_NAME]
except Exception as e:
    print('Error:', e)
    sys.exit(1)

MAIL_COLLECTION = DB.mail
