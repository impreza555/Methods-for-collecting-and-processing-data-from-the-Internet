import json
import os
import re
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlencode

import scrapy
from dotenv import load_dotenv
from scrapy.http import HtmlResponse

from instagram.items import InstagramItem


class InstaParseSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    load_dotenv(dotenv_path=Path('.') / '.env')
    insta_login = os.getenv('login')
    insta_pwd = os.getenv('password')
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    def __init__(self, users_list):
        self.parse_users = users_list

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        var_subscribers = {'search_surface': 'follow_list_page', 'count': 12}
        var_subscriptions = {'count': 12}
        url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?' \
                          f'{urlencode(var_subscribers)}'
        url_subscriptions = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?' \
                            f'{urlencode(var_subscriptions)}'
        yield response.follow(
            url_subscribers,
            callback=self.subscribers_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(var_subscribers)
                       }
        )
        yield response.follow(
            url_subscriptions,
            callback=self.subscriptions_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(var_subscriptions)
                       }

        )

    def subscribers_parse(self, response: HtmlResponse, user_id, username, variables):
        j_body = json.loads(response.text)
        if response.status == 200:
            variables['max_id'] = + variables['count']
            url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}'
            yield response.follow(
                url_subscribers,
                callback=self.subscribers_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )
        subscribers = j_body.get('users')
        for subscriber in subscribers:
            item = InstagramItem(
                source_id=user_id,
                source_name=username,
                user_id=subscriber.get('pk'),
                user_name=subscriber.get('username'),
                user_fullname=subscriber.get('full_name'),
                photo_url=subscriber.get('profile_pic_url'),
                subs_type='subscriber'
            )
            yield item

    def subscriptions_parse(self, response: HtmlResponse, user_id, username, variables):
        j_body = json.loads(response.text)
        if response.status == 200:
            variables['max_id'] = + variables['count']
            url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}'
            yield response.follow(
                url_subscribers,
                callback=self.subscribers_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )
        subscriptions = j_body.get('users')
        for subscription in subscriptions:
            item = InstagramItem(
                source_id=user_id,
                source_name=username,
                user_id=subscription.get('pk'),
                user_name=subscription.get('username'),
                user_fullname=subscription.get('full_name'),
                photo_url=subscription.get('profile_pic_url'),
                subs_type='subscription'
            )
            yield item

    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    @staticmethod
    def fetch_user_id(text, username):
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')
