from copy import deepcopy

import scrapy
from scrapy.http import HtmlResponse

from job_parser.items import JobParserItem


class HhruSpider(scrapy.Spider):
    name = 'prombez24'
    allowed_domains = ['prombez24.com']

    def __init__(self, start_url, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [start_url]

    def parse(self, response: HtmlResponse):
        links = response.xpath("//ul[contains(@class, 'double-col')]//a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response):
        question_cards = response.xpath("//div[@class='question row']")
        for _card in question_cards:
            question_number = _card.css('.question__number::text').extract_first()
            question_text = _card.css('.question__text::text').extract_first()
            answers = _card.css('input[name$="answerText"]::attr(value)').getall()
            correct = _card.css('input[name$="correct"]::attr(value)').getall()

            yield JobParserItem(question_number=question_number,
                                question_text=question_text,
                                answers=answers,
                                correct=correct)
