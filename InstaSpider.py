import scrapy


class InstaspiderSpider(scrapy.Spider):
    name = 'InstaSpider'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    def parse(self, response):
        pass
