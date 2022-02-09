import scrapy


class BooksItem(scrapy.Item):
    link_to_book = scrapy.Field()
    book_title = scrapy.Field()
    authors = scrapy.Field()
    price_base = scrapy.Field()
    price_discount = scrapy.Field()
    book_rating = scrapy.Field()
    _id = scrapy.Field()
