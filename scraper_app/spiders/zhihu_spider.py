#-*- coding:utf-8 –*-

import json
from datetime import date
from scrapy import Spider,  Request
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose
from scrapy.http import FormRequest
from scraper_app.items import ZhihuAnswer


class ZhihuSpider(Spider):
    """Spider for poular answers from zhihu.com"""
    name = "zhihu"
    allowed_domains = ["zhihu.com"]

    # start with captcha page to get the login captcha
    start_urls = ["http://www.zhihu.com/captcha.gif"]

    # define Xpath to extact answers
    answers_list_xpath = "//div[@class='explore-feed feed-item']"

    # scrape info for each answer
    question = ".//h2/a/text()"
    question_link = ".//h2/a/@href"

    # notice the space after zm-item-answser, Zhihu is naughty
    author = ".//div[@class='zm-item-answer ']/div[@class='answer-head']" + \
        "/div[@class='zm-item-answer-author-info']/h3/a/text()"
    author_link = ".//div[@class='zm-item-answer ']/div[@class='answer-head']" + \
        "/div[@class='zm-item-answer-author-info']/h3/a/@href"
    vote = ".//div[@class='zm-item-answer ']/div[@class='zm-item-vote']/a/@data-votecount"
    summary = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text']" + \
        "/div[@class='zh-summary summary clearfix']/text()"
    answer = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text']" + \
        "/textarea[@class='content hidden']/text()"

    item_fields = {
        "question": question,
        "question_link": question_link,
        "author": author,
        "author_link": author_link,
        "vote": vote,
        "summary": summary,
        "answer": answer
    }

    def parse(self, response):
        """
        Method that performs Zhihu user login.
        """

        # save captcha img on disk
        with open("captcha.gif", "wb") as f:
            f.write(response.body)

        # user has to enter captcha manually
        captcha = raw_input("Please enter captcha: ")

        # login
        return [FormRequest(url="http://www.zhihu.com/login/email",
                            formdata={"email": "bestofzhihu@gmail.com",
                                      "password": "shehuizhuyihao",
                                      "captcha": captcha},
                            callback=self.after_login)]

    def after_login(self, response):
        # check if login is successful
        login_status = json.loads(response.body)

        if login_status["r"]:
            self.logger.error("Login failed.")
            return

        # we will parse the hottest answers by day and month
        for time in ["day", "month"]:
            for offset in range(0, 50, 5):
                params = '"offset": {0}, "type": "{1}"'.format(offset, time)
                url = 'http://www.zhihu.com/node/ExploreAnswerListV2?params={' + params + '}'
                yield Request(url, callback=self.parse_answers)

    def parse_answers(self, response):
        # use selector to extract answers
        selector = Selector(response)

        # iterate over answers
        for answer in selector.xpath(self.answers_list_xpath):
            loader = ItemLoader(item=ZhihuAnswer(), selector=answer)

            # define processors
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            # iterate over fields and add xpaths to the loader
            for field, xpath in self.item_fields.iteritems():
                loader.add_xpath(field, xpath)

            item = loader.load_item()

            # convert the full text of answer into html
            item["answer"] = item["answer"].encode('ascii', 'xmlcharrefreplace')

            # change vote to integer
            item["vote"] = int(item["vote"])

            # in case of anonymous authors
            if "author" not in item:
                item["author"] = u'匿名用户'

            # complete links
            item["question_link"] = u"http://www.zhihu.com" + item["question_link"]

            if "author_link" in item:
                item["author_link"] = u"http://www.zhihu.com" + item["author_link"]
            else:
                item["author_link"] = ""

            # add the date when scraped
            item["date"] = date.today()

            yield item
