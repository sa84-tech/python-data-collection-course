import scrapy
from scrapy.http import HtmlResponse

from job_parser.items import JobParserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python',]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class, '-Dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[contains(@class, 'vacancy-item')]//a[contains(@href, 'vakansii')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//h1/../span//text()").getall()
        link = response.url
        yield JobParserItem(name=name, salary=salary, link=link)
