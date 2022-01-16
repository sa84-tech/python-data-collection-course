# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Identity, Compose


def clear_price(value):
    value = re.sub(r'\s+', '', value, flags=re.UNICODE)
    try:
        value = float(value)
    except:
        pass
    finally:
        return value


def clear_catalog(value):
    value = '/'.join(value[2:])
    return value


class LeroyParserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clear_price), output_processor=TakeFirst())
    category = scrapy.Field(input_processor=Compose(clear_catalog), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
    _id = scrapy.Field()
