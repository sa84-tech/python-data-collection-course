# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_URI = os.environ.get('DB_URI')
DB_NAME = os.environ.get('DB_NAME')


class JobParserPipeline:
    def __init__(self):
        client = MongoClient(DB_URI)
        self.mongobase = client.job_parser_scrapy

    def process_item(self, item, spider):
        item['min'], item['max'], item['cur'] = self.process_salary(item['salary'])
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_salary(self, salary):
        return 10, 20, 'руб.'
