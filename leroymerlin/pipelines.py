import scrapy
import re
import os
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        item['_id'] = item['_id'][0]
        item['price'] = item['price'][0]
        item['characteristic'] = {
            item['terms'][i]: item['definitions'][i] for i in range(len(item['terms']))
        }
        del item['terms'], item['definitions']
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item


class LeroymerlinImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        pattern = re.compile('\/(\d+)')
        name = re.findall(pattern, request.url)[0]
        path = f'{os.getcwd()}\\photos\\{name}\\'
        if os.path.exists(path) == False:
            os.mkdir(path)
        tail = os.path.basename(request.url)
        result = f'{path}{tail}'
        return result

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
