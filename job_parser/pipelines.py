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
        item['min'], item['max'], item['cur'] = self.process_salary_hh(item['salary']) \
            if spider.name == 'hhru' \
            else self.process_salary_superjob(item['salary'])
        item['_id'] = hashlib.md5(item['link'].encode()).hexdigest()
        del item['salary']
        collection = self.mongobase[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item

    def process_salary_hh(self, salary):
        salary_str = re.sub(r'\s+', '', ''.join(salary), flags=re.UNICODE)

        if re.search('з/п', salary_str):
            return 0.0, 0.0, None

        min_sal = 0.0
        max_sal = 0.0
        cur_sal = salary[-2]

        values = [float(s) for s in re.findall(r'-?\d+\.?\d*', salary_str)]

        if re.search(r'от\d*до', salary_str):
            min_sal = values[0]
            max_sal = values[1]
        elif re.search(r'от\d', salary_str):
            min_sal = values[0]
        elif re.search(r'до\d', salary_str):
            max_sal = values[0]

        return min_sal, max_sal, cur_sal

    def process_salary_superjob(self, salary):
        salary_str = re.sub(r'\s+', '', ''.join(salary), flags=re.UNICODE)

        if 'договор' in salary_str:
            return 0.0, 0.0, None

        min_sal = 0.0
        max_sal = 0.0
        cur_sal = ''

        values = [float(s) for s in re.findall(r'-?\d+\.?\d*', salary_str)]

        if len(values) == 2:
            min_sal = values[0]
            max_sal = values[1]
        elif re.search(r'от\d', salary_str):
            min_sal = values[0]
        elif re.search(r'до\d', salary_str):
            max_sal = values[0]

        if re.search('руб.', salary_str):
            cur_sal = 'руб.'
        elif re.search('USD', salary_str):
            cur_sal = 'USD'
        elif re.search('EUR', salary_str):
            cur_sal = 'EUR'

        return min_sal, max_sal, cur_sal
