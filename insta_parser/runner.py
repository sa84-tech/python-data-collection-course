from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from insta_parser import settings
from insta_parser.spiders.InstaSpider import InstaSpider

if __name__ == '__main__':
    search = ''

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider, search)

    process.start()
