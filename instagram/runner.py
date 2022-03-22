from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import settings
from instagram.spiders.insta_parse import InstaParseSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    # users_list = input('Введите имена пользователей через запятую: ').split(',')
    # process.crawl(InstaParseSpider, users_list)
    process.crawl(InstaParseSpider, users_list=['metallica', 'ironmaiden'])  # у Металлики и Иронмейден очень много подписчиков. Лучше своих указать.)
    process.start()
