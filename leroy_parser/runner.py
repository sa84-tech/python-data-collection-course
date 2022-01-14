from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroy_parser import settings
from leroy_parser.spiders.LeroyMerlin import LeroymerlinSpider

if __name__ == '__main__':
    search = 'Кухни'

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, search)

    process.start()
