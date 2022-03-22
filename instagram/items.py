import scrapy


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    source_id = scrapy.Field()
    source_name = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_fullname = scrapy.Field()
    photo_url = scrapy.Field()
    subs_type = scrapy.Field()
