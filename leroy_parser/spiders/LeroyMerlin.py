import scrapy


class LeroymerlinSpider(scrapy.Spider):
    name = 'LeroyMerlin'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = ['https://spb.leroymerlin.ru/catalogue/mebel-dlya-vannoy-komnaty/']

    def __init__(self, category, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://spb.leroymerlin.ru/catalogue/{category}/']

    def parse(self, response):
        print()
