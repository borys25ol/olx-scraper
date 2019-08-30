# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy import Request


class OlxPkSpider(scrapy.Spider):
    name = 'olx.pk'

    allowed_domains = ['olx.com.pk']

    start_urls = [
        'https://www.olx.com.pk/property-for-rent_c3',
    ]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    products_on_page_re = re.compile('(.+) ads in')

    def __init__(self):
        super(OlxPkSpider, self).__init__()
        self.olx_api_pattern = 'https://www.olx.com.pk/api/locations?parent={location}'
        self.olx_page_pattern = 'https://www.olx.com.pk/{}{}'

    @staticmethod
    def get_data_from_json(response):
        data = json.loads(response.text)
        data = data.get('data')
        return data

    @staticmethod
    def make_url(url_pattern, name, location_id, head):
        name = name.lower().replace(' ', '-')
        id_part = '_g' + str(location_id)
        url = url_pattern.format(name, id_part) + head
        return url

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        categories_urls = response.xpath('//ul[@data-aut-id="subcategories"]/li/ul/li/a')

        for url in categories_urls:
            yield response.follow(url=url, callback=self.parse_category)

    def parse_category(self, response):
        numbers = re.findall('\d+', response.url)
        location_id = numbers[0]
        category_id = numbers[-1]

        products_count = response.css('p.FYmzo::text').re_first(self.products_on_page_re)
        if products_count:
            products_count = products_count.replace(',', '')
            count = int(products_count)

            if count and count > 2000:
                if response.url.endswith('/'):
                    response.meta['path'] = '/' + response.url.split('/')[-2]
                else:
                    response.meta['path'] = '/' + response.url.split('/')[-1]
                if category_id == location_id:
                    url = self.olx_api_pattern.format(location='1000001')
                else:
                    url = self.olx_api_pattern.format(location=location_id)

                yield response.request.replace(
                    url=url,
                    callback=self.parse_olx_api,
                    meta=response.meta
                )

    def parse_olx_api(self, response):
        head_path = response.meta.get('path')
        data = self.get_data_from_json(response)
        if data:
            id_list = [(item['id'], item['name']) for item in data]
            for id, name in id_list:
                url = self.make_url(self.olx_page_pattern, name, id, head_path)
                yield response.request.replace(
                    url=url,
                    callback=self.parse_category
                )
