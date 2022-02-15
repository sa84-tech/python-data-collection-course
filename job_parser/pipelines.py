# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import re

from itemadapter import ItemAdapter
import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_URI = os.environ.get('DB_URI')


class JobParserPipeline:
    def __init__(self):
        client = MongoClient(DB_URI)
        self.collection = client.prom_bez['group-3-up-to-1000V']

    def process_item(self, item, spider):
        # print('PREV ITEM:', item)
        item['_id'] = hashlib.md5(item['question_text'].encode()).hexdigest()
        item['question_number'] = int(item['question_number'].split('#')[-1])
        item['correct_answers'] = [ans for i, ans in enumerate(item['answers']) if item['correct'][i] == 'true']
        del item['answers']
        del item['correct']
        self.collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        # print('FINAL ITEM:', item)
        return item
