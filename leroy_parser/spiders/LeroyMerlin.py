import scrapy
from scrapy.http import HtmlResponse


class LeroymerlinSpider(scrapy.Spider):
    name = 'LeroyMerlin'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = ['https://spb.leroymerlin.ru/catalogue/mebel-dlya-vannoy-komnaty/']

    def __init__(self, category, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://spb.leroymerlin.ru/catalogue/{category}/']

    def parse(self, response):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='product-image']")
        for link in links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        price = response.xpath("//span[@slot='price']/text()").get()
        link = response.url
        print()

