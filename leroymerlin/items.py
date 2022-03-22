import scrapy
import hashlib
import re
from itemloaders.processors import MapCompose, TakeFirst, Compose


def clean_price(value):
    value = value.replace(' ', '')
    try:
        value = int(value)
    except:
        return value
    return value


def get_id(value):
    _id = hashlib.md5(str(value).encode('utf-8')).hexdigest()
    return _id


def edit_definitions(values):
    pattern = re.compile('\\n +')
    values = re.sub(pattern, '', values)
    try:
        return float(values)
    except ValueError:
        return values


class LeroymerlinItem(scrapy.Item):
    _id = scrapy.Field(input_processor=MapCompose(get_id))
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clean_price))
    url = scrapy.Field(output_processor=TakeFirst())
    terms = scrapy.Field(input_processor=MapCompose())
    definitions = scrapy.Field(input_processor=MapCompose(edit_definitions))
    photos = scrapy.Field(input_processor=MapCompose())
    characteristic = scrapy.Field()
