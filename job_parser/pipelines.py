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
        self.mongobase = client.job_parser_scrapy

    def process_item(self, item, spider):
        print(item)
        item['_id'] = hashlib.md5(item['question_text'].encode()).hexdigest()
        item['question_number'] = int(item['question_number'].split('#')[-1])
        # collection = self.mongobase['PromBez24']
        # collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        print(item)
        return item
