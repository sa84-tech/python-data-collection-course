# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import os

import scrapy
from dotenv import load_dotenv
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DB_URI = os.environ.get('DB_URI')


class InstaParserPipeline:
    def __init__(self):
        client = MongoClient(DB_URI)
        self.researched_collection = client.insta_parser['researched_users']
        self.related_collection = client.insta_parser['related_users']

    def process_item(self, item, spider):
        item['_id'] = hashlib.md5(str(item['user_id']).encode()).hexdigest()

        if item['data_type'] == 'researched_user':
            del item['data_type']
            self.researched_collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

        else:
            ref_user_id = hashlib.md5(str(item['ref_user_id']).encode()).hexdigest()
            field_name = item['data_type']
            del item['ref_user_id'], item['data_type']

            self.related_collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
            self.researched_collection.update_one({'_id': ref_user_id},
                                                  {'$addToSet': {field_name: item['_id']}}, upsert=True)

        return item


class InstaImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photo'] = results[0][1]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        if item['data_type'] == 'researched_user':
            return f'researched_users/{item["username"]}.jpg'
        return f'related_users/{item["username"]}.jpg'
