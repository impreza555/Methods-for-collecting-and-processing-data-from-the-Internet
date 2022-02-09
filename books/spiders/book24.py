import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from books.items import BooksItem

edge_options = Options()
edge_options.add_argument("start-maximized")


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']

    def __init__(self, keyword, **kwargs):
        self.keyword = keyword
        self.i = 1
        self.start_urls = [f'https://book24.ru/search/?q={self.keyword}']
        super().__init__(**kwargs)

    def parse(self, response: HtmlResponse):
        self.i += 1
        if response.status == 200:
            next_page = f'https://book24.ru/search/page-{self.i}/?q={self.keyword}'
            yield response.follow(next_page, callback=self.parse)
        book_links = response.xpath(
            '//div[@class="product-list__item"]//a[contains(@class, "product-card__image-link")]/@href').getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

    def parse_book(self, response: HtmlResponse):
        book_title = response.xpath('//h1//text()').get()
        link_to_book = response.url
        driver = webdriver.Edge(executable_path='./msedgedriver', options=edge_options)
        driver.get(link_to_book)
        try:
            elems = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH,
                     '//div[@class="product-detail-page__preview-info-holder"]//span[normalize-space()="Автор:"]/../../div[position()=2]')
                )
            )
            authors = [_.text for _ in elems]
        finally:
            driver.quit()
        price_base = response.xpath(
            '//div[@class="product-sidebar product-detail-page__sidebar"]//span[@class="app-price product-sidebar-price__price-old"]/text()').get()
        price_discount = response.xpath(
            '//div[@class="product-sidebar product-detail-page__sidebar"]//span[@class="app-price product-sidebar-price__price"]/text()').get()
        if price_base is None:
            price_base = price_discount
            price_discount = None
        book_rating = response.xpath(
            '//div[@itemprop="aggregateRating"]//span[@class="rating-widget__main-text"]/text()').get()
        yield BooksItem(link_to_book=link_to_book, book_title=book_title, authors=authors, price_base=price_base,
                        price_discount=price_discount, book_rating=book_rating)
