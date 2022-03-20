import scrapy


class InstaParseSpider(scrapy.Spider):
    name = 'insta_parse'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    def parse(self, response):
        pass
