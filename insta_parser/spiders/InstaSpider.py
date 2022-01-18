import scrapy
from scrapy.http import HtmlResponse


class InstaSpider(scrapy.Spider):
    name = 'InstaSpider'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']

    def parse(self, response: HtmlResponse):
        pass
