import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroyMerlinSpider(scrapy.Spider):
    name = 'leroy_merlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, category, **kwargs):
        super().__init__(**kwargs)
        self.category = category
        self.i = 1
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{self.category}/?page={self.i}']

    def parse(self, response: HtmlResponse):
        self.i += 1
        if response.xpath('//a[contains(@aria-label, "Следующая страница")]'):
            next_page = f'https://leroymerlin.ru/catalogue/{self.category}/?page={self.i}'
            yield response.follow(next_page, callback=self.parse)
        product_links = response.xpath('//a[@data-qa="product-name"]/@href').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_products)

    def parse_products(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_value('_id', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('photos', '//picture/source[@media=" only screen and (min-width: 1024px)"]/@srcset')
        loader.add_xpath('terms', "//dt/text()")
        loader.add_xpath('definitions', "//dd/text()")
        loader.add_value('url', response.url)
        yield loader.load_item()
