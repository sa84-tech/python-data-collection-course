# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import os
import re

import scrapy
from dotenv import load_dotenv
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
DB_URI = os.environ.get('DB_URI')


def clear_name(file_name, replace_slash=True):
    quotes = """“”«»'\""""
    file_name = re.sub(r'[' + quotes + ']', '', file_name)
    if replace_slash:
        file_name = re.sub(r'[/]', '-', file_name)
    file_name = re.sub(r'[|*?<>:\\\n\r\t\v]', '', file_name)
    file_name = re.sub(r'\s{2,}', ' ', file_name)
    file_name = file_name.strip()
    file_name = re.sub(r'\s', '_', file_name)

    ls = file_name[-1]
    while ls == '-' or ls == '.':
        file_name = file_name.rstrip('-')
        file_name = file_name.rstrip('.')
        file_name = file_name.rstrip()
        ls = file_name[-1]
    return file_name


class LeroyParserPipeline:
    def __init__(self):
        client = MongoClient(DB_URI)
        self.collection = client.leroy_parser['catalog']

    def process_item(self, item, spider):
        item['_id'] = hashlib.md5(item['link'].encode()).hexdigest()
        self.collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item


class LeroyImagesPipeLine(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['images']:
            for image in item['images']:
                try:
                    yield scrapy.Request(image)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['images'] = [i[1] for i in results if i[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        category = clear_name(item["category"], False)
        name = clear_name(item["name"])
        return f'{category}/{name}/{image_guid}.jpg'
