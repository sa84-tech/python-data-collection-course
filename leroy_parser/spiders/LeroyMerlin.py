import scrapy


class LeroymerlinSpider(scrapy.Spider):
    name = 'LeroyMerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']

    def parse(self, response):
        pass
