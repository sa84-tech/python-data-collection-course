import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroy_parser.items import LeroyParserItem


class LeroymerlinSpider(scrapy.Spider):
    name = 'LeroyMerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://spb.leroymerlin.ru/search/?q={search}']

    def parse(self, response):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='product-image']")
        for link in links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyParserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        # loader.add_xpath('category', "(//a[@data-division])[last()]/@data-division")
        loader.add_xpath('category', "//a[@data-division]/@data-division")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('images', "//source[contains(@media, '1024px')]/@srcset")
        loader.add_value('link', response.url)
        yield loader.load_item()

        # name = response.xpath("//h1/text()").get()
        # price = response.xpath("//span[@slot='price']/text()").get()
        # images = response.xpath("//source[contains(@media, '1024px')]/@srcset").getall()
        # category = response.xpath("(//a[@data-division])[last()]/@data-division").get()
        # link = response.url
        # yield LeroyParserItem(name=name, price=price, images=images, link=link)
