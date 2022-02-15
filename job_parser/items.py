# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobParserItem(scrapy.Item):
    # define the fields for your item here like:
    question_number = scrapy.Field()
    question_text = scrapy.Field()
    answers = scrapy.Field()
    correct = scrapy.Field()
    correct_answers = scrapy.Field()
    _id = scrapy.Field()
