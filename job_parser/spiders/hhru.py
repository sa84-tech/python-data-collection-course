import scrapy
from scrapy.http import HtmlResponse

from job_parser.items import JobParserItem


class HhruSpider(scrapy.Spider):
    name = 'prombez24'
    allowed_domains = ['prombez24.com']
    start_urls = ['https://prombez24.com/tests/208']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//ul[contains(@class, 'double-col')]//a/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        question_cards = response.xpath("//div[@class='question row']")

        for card in question_cards:
            answers = []
            question_number = card.css('.question__number::text').extract_first()
            question_text = card.css('.question__text::text').extract_first()
            all_answers = card.xpath('//div[@class="question__answers-list"]')

            for answer in all_answers:
                answer_data = {'text': answer.css('input[name="questionList[3].answers[0].answerText"]::attr(value)') \
                    .extract_first(),
                               'is_correct': answer.css('input[name="questionList[3].answers[0].correct"]::attr(value)') \
                                   .extract_first()}
                print('*** ANSWER DATA:', answer_data)
                answers.append(answer_data)

            yield JobParserItem(question_number=question_number,
                                question_text=question_text,
                                answers=answers)

    # def vacancy_parse(self, response: HtmlResponse):
    #     name = response.xpath("//h1//text()").get()
    #     salary = response.xpath("//div[@data-qa='vacancy-salary']//text()").getall()
    #     link = response.url
    #     yield JobParserItem(name=name, salary=salary, link=link)
