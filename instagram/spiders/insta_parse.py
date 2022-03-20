import os
import re
import json
import scrapy
from dotenv import load_dotenv
from pathlib import Path
from scrapy.http import HtmlResponse
from instagram.items import InstagramItem


class InstaParseSpider(scrapy.Spider):
    name = 'insta_parse'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    load_dotenv(dotenv_path=Path('.') / '.env')
    login = os.getenv('login')
    password = os.getenv('password')

    def __init__(self, users_list):
        self.parse_users = users_list

    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.login, 'enc_password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    def login(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )
