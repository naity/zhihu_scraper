from scrapy import Item, Field


class ZhihuAnswer(Item):
    """Zhihu container for scraped data"""
    question = Field()
    question_link = Field()
    author = Field()
    author_link = Field()
    vote = Field()
    summary_img = Field()
    summary_text = Field()
    answer = Field()
    date = Field()
