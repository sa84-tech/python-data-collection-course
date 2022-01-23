import json
import os
import re
from copy import deepcopy

import scrapy
from scrapy.http import HtmlResponse
from dotenv import load_dotenv
from urllib.parse import urlencode

from insta_parser.items import InstaParserItem

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

INSTA_USERNAME = os.environ.get('INSTA_USERNAME')
INSTA_PASSWORD = os.environ.get('INSTA_ENCRYPTED_PASSWORD')


class InstaSpider(scrapy.Spider):
    name = 'InstaSpider'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    instagram_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    instagram_username = INSTA_USERNAME
    instagram_enc_password = INSTA_PASSWORD
    parse_user = 'ai_machine_learning'
    query_link = '/graphql/query/?'
    api_link = 'https://i.instagram.com/api/v1/'
    query_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def __init__(self, parse_users):
        self.parse_users = parse_users

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.instagram_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.instagram_username, 'enc_password': self.instagram_enc_password},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        json_data = response.json()
        if json_data.get('authenticated'):
            for user in self.parse_users:
                yield response.follow(f'/{user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        headers = {'User-Agent': 'Instagram 155.0.0.37.107'}

        ulr_user_info = f'{response.url}?__a=1'
        yield response.follow(ulr_user_info,
                              callback=self.user_info_parse,
                              cb_kwargs={'username': username, 'user_id': user_id})

        vars_followers = {'count': 12, 'search_surface': 'follow_list_page'}
        url_followers = f'{self.api_link}friendships/{user_id}/followers/?{urlencode(vars_followers)}'
        yield response.follow(url_followers,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username, 'user_id': user_id,
                                         'variables': deepcopy(vars_followers)},
                              headers=headers)

        vars_following = {'count': 12}
        url_following = f'{self.api_link}friendships/{user_id}/following/?{urlencode(vars_following)}'

        yield response.follow(url_following,
                              callback=self.user_following_parse,
                              cb_kwargs={'username': username, 'user_id': user_id,
                                         'variables': deepcopy(vars_following)},
                              headers=headers)

    def user_info_parse(self, response: HtmlResponse, username, user_id):
        user_info = response.json().get('graphql').get('user')
        full_name = user_info.get('full_name'),
        photo = user_info.get('profile_pic_url_hd'),
        item = InstaParserItem(
            data_type='researched_user',
            user_id=user_id,
            username=username,
            full_name=full_name[0],
            photo=photo[0],
        )
        yield item

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables):
        json_data = response.json()
        next_max_id = json_data.get('next_max_id')
        json_data.get('next_max_id')
        if next_max_id:
            variables['max_id'] = next_max_id
            url_followers = f'{self.api_link}friendships/{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        users = json_data.get('users')
        for user in users:
            item = InstaParserItem(
                data_type='followers',
                ref_user_id=user_id,
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
            )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables):
        json_data = response.json()
        next_max_id = json_data.get('next_max_id')
        json_data.get('next_max_id')
        if next_max_id:
            variables['max_id'] = next_max_id
            url_following = f'{self.api_link}friendships/{user_id}/following/?{urlencode(variables)}'

            yield response.follow(url_following,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'username': username, 'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        users = json_data.get('users')
        for user in users:
            item = InstaParserItem(
                data_type='following',
                ref_user_id=user_id,
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
            )
            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
