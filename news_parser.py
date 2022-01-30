import hashlib

import requests
from lxml import html
from pymongo import MongoClient
from pymongo import errors
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = MongoClient('localhost', 27017)
db = client['news']
news_mail_ru = db.news_mail_ru


def new_parser():
    url = 'https://news.mail.ru/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/83.0.4254.19'
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, headers=headers)
    dom = html.fromstring(response.text)
    links = dom.xpath(
        ".//div[contains(@class,'daynews__item')]//a[contains(@class,'photo_scale')]|//li[@class='list__item']/a[@class='list__text']")
    list_links = []

    for link in links:
        list_links.append(link.xpath(".//@href")[0])
    for link in list_links:
        news = {}
        response = session.get(link, headers=headers)
        dom = html.fromstring(response.text)
        source_name = dom.xpath(".//a[@class='link color_gray breadcrumbs__link']/span[@class='link__text']/text()")
        news_headline = dom.xpath(".//h1/text()")
        link_to_news = link
        publication_date = dom.xpath(".//span[@class='note__text breadcrumbs__text js-ago']/@datetime")
        news['source_name'] = source_name[0].replace('© ', '')
        news['news_headline'] = news_headline[0]
        news['link_to_news'] = link_to_news
        news['publication_date'] = publication_date[0][:10]
        id = hashlib.md5(str(news).encode('utf-8')).hexdigest()
        news['_id'] = id
        try:
            news_mail_ru.insert_one(news)
        except errors.DuplicateKeyError:
            print(f'Новость уже существует в базе')
            continue


if __name__ == "__main__":
    new_parser()
