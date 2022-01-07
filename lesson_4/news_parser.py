from datetime import datetime
import os
import sys
import hashlib

import requests
from pprint import pprint
from lxml import html
from pymongo import MongoClient
from dotenv import load_dotenv
from dateparser import parse as parse_date

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


URL = 'https://lenta.ru'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.71 Safari/537.36'}

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


def parse_link(link_str):
    if link_str[:4] == 'http':
        split_link = link_str.split('/')
        source = f'{split_link[0]}//{split_link[2]}'
        link = link_str
    else:
        source = URL
        link = URL + link_str
    
    return source, link


response = requests.get(URL, headers=HEADERS)
dom = html.fromstring(response.text)

items = dom.xpath('//a[contains(@class,"_topnews")]')

news = []

for item in items:
    news_item = {}

    title = item.xpath('.//h3/text()|.//span/text()')[0]
    href = item.xpath('./@href')[0]
    time = item.xpath('.//time/text()')[0]

    source, link = parse_link(href)

    news_item['_id'] = hashlib.md5(link.encode()).hexdigest()
    news_item['title'] = title
    news_item['source'] = source
    news_item['link'] = link
    news_item['date'] = parse_date(time, settings={'RETURN_AS_TIMEZONE_AWARE': True,
                                                   'RELATIVE_BASE': datetime.now()})

    news.append(news_item)
    NEWS_COLLECTION.update_one({'_id': news_item['_id']}, {'$set': news_item}, upsert=True)

pprint(news)
