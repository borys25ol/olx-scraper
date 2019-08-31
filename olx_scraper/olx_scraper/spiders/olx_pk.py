# -*- coding: utf-8 -*-
import json
import re
from math import ceil

import scrapy
from scrapy import Request
from w3lib.url import add_or_replace_parameter


class OlxPkSpider(scrapy.Spider):
    name = 'olx.pk'

    allowed_domains = ['olx.com.pk']

    start_urls = [
        'https://www.olx.com.pk/property-for-rent_c3',
    ]

    extra_links = [
        # 'https://www.olx.com.pk/sindh_g2003007/apartments-flats_c1723'
    ]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    products_on_page_re = re.compile('(.+) ads in')

    def __init__(self):
        super(OlxPkSpider, self).__init__()
        self.filter = set()
        self.olx_api_pattern = 'https://www.olx.com.pk/api/locations?parent={location}'
        self.olx_page_pattern = 'https://www.olx.com.pk/{}{}'
        self.olx_product_pattern = 'https://www.olx.com.pk/item/{id}'
        self.olx_category_api_url = 'https://www.olx.com.pk/api/relevance/search'

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

    @staticmethod
    def create_category_api_url(url_pattern, **kwargs):
        url = url_pattern

        payload = {
            'category': kwargs['category_id'],
            'facet_limit': '100',
            'location': kwargs['location'],
            'location_facet_limit': '6',
            'page': kwargs['page'],
            'user': '16a55be26b4x3d2ccfc'
        }

        if kwargs.get('sorting'):
            payload.update({
                'sorting': kwargs['sorting']
            })

        for k, v in payload.items():
            url = add_or_replace_parameter(url, k, v)

        return url

    def start_requests(self):
        if self.extra_links:
            for url in self.extra_links:
                yield Request(url=url, callback=self.parse_category)
        else:
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

                location = '1000001' if category_id == location_id else location_id
                url = self.olx_api_pattern.format(location=location)

                yield response.request.replace(
                    url=url,
                    callback=self.parse_olx_api,
                    meta=response.meta
                )
            else:
                if count and count > 1000:
                    total_pages = ceil(ceil(count / 20) / 2)
                    for page in range(int(total_pages)):
                        for sorting in ['asc-price', 'desc-price']:
                            url = self.create_category_api_url(
                                url_pattern=self.olx_category_api_url,
                                category_id=category_id,
                                page=page,
                                location='1000001' if category_id == location_id else location_id,
                                sorting=sorting
                            )
                            yield response.request.replace(
                                url=url,
                                callback=self.parse_api_id,
                                meta=response.meta
                            )

                if count and count <= 1000:
                    total_pages = ceil(count / 20)
                    for page in range(int(total_pages)):
                        url = self.create_category_api_url(
                            url_pattern=self.olx_category_api_url,
                            category_id=category_id,
                            page=page,
                            location='1000001' if category_id == location_id else location_id,
                        )
                        yield response.request.replace(
                            url=url,
                            callback=self.parse_api_id,
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

    def parse_api_id(self, response):
        data = self.get_data_from_json(response)
        if data:
            id_list = [item['id'] for item in data]
            for id in id_list:
                product_page = self.olx_product_pattern.format(id=id)
                if product_page not in self.filter:
                    self.filter.add(product_page)
                    response.meta['_origin_url'] = product_page
                    yield response.request.replace(
                        url=product_page,
                        callback=self.parse_page_info,
                        meta=response.meta
                    )

    def parse_page_info(self, response):
        pass
