# -*- coding: utf-8 -*-
import datetime
import json
import re
from math import ceil

import scrapy
from scrapy import Request
from w3lib.url import add_or_replace_parameter

from olx_scraper.items import ErrorItem, OlxItemLoader, UserItem, OlxItem


class OlxPkSpider(scrapy.Spider):
    name = 'olx.pk'

    allowed_domains = ['olx.com.pk']

    start_urls = [
        'https://www.olx.com.pk/property-for-rent_c3',
    ]

    extra_links = [
        # 'https://www.olx.com.pk/sindh_g2003007/apartments-flats_c1723'
    ]

    products_on_page_re = re.compile('(.+) ads in')

    image_urls_re = re.compile('background-image:url\((.+)\)')
    count_of_images_re = re.compile('\d+\s+/\s+(\d+)')
    location_re = re.compile('(.+),.+,.+')
    city_re = re.compile('.+,(.+),.+')
    province_re = re.compile('.+,.+,(.+)')
    phone_number_re = re.compile('"key_name":"phone","value":"(\+\d+)"')
    date_on_website_re = re.compile('"created_at_first":"(.+?)"')
    number_account_re = re.compile('profile/(\d+)')

    breadcrumb_xpath = '//ol/li/a'
    image_urls_xpath_1 = '//*[@id="container"]/main/div/div/div[4]/div/div/div[4]/div/div/div//button/@style'
    image_urls_xpath_2 = '//div[@class="slick-track"]//img/@src'
    count_of_images_xpath = '//div[contains(@class, "slick-slider")]/..//span'
    featured_xpath = '//span[contains(text(), "Featured")]'
    description_xpath = '//div[@data-aut-id="itemDescriptionContent"]'
    price_xpath = '//span[@data-aut-id="itemPrice"]'
    title_xpath = '//h1[@data-aut-id="itemTitle"]'
    location_xpath = '//h3[contains(text(), "Posted in")]/..//following-sibling::div/span'
    agent_name_xpath = '//div[@data-aut-id="profileCard"]//a/div'
    purpose_xpath = '//li/a[contains(text(), "Property")]'
    property_type_xpath = '//li/a[contains(text(), "Property")]/../../li[last()]/a'
    area_xpath = '//span[@data-aut-id="key_ft"]/../span[@data-aut-id="value_ft"]'
    area_unit_xpath = '//span[@data-aut-id="key_ft_unit"]/../span[@data-aut-id="value_ft_unit"]'
    bedroom_xpath = '//span[@data-aut-id="key_rooms"]/../span[@data-aut-id="value_rooms"]'
    ad_id_xpath = '//strong[contains(text(), "AD ID")]'
    date_on_website_xpath = '//div[@data-aut-id="itemCreationDate"]/span'
    agent_url_xpath = '//div[@data-aut-id="profileCard"]//a/@href'

    user_name_xpath = '//div[@data-aut-id="profileHeader"]/div'
    verified_number_xpath = '//div[@data-aut-id="verifiedAccount"]//div[@class="_1IG2d"]'
    since_date_xpath = '//div[@data-aut-id="memberSince"]//span/span'

    def __init__(self):
        super(OlxPkSpider, self).__init__()
        self.filter = set()
        self.handle_httpstatus_list = [404, 403, 503, 500, 400]
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
        l = OlxItemLoader(item=OlxItem(), response=response)

        l.add_xpath('breadcrumb', self.breadcrumb_xpath)
        l.add_xpath('image_urls', self.image_urls_xpath_1, re=self.image_urls_re)

        if not l.get_output_value('image_urls'):
            l.add_xpath('image_urls', self.image_urls_xpath_2)
            l.add_value('count_of_images', '1')

        l.add_xpath('count_of_images', self.count_of_images_xpath, re=self.count_of_images_re)

        featured = l.get_xpath(self.featured_xpath)
        result = 'yes' if featured else 'no'
        l.add_value('featured', result)

        l.add_xpath('description', self.description_xpath)
        l.add_xpath('price', self.price_xpath)
        l.add_xpath('title', self.title_xpath)

        l.add_xpath('location', self.location_xpath, re=self.location_re)
        l.add_xpath('city', self.location_xpath, re=self.city_re)
        l.add_xpath('province', self.location_xpath, re=self.province_re)

        l.add_value('phone_number', self.phone_number_re.findall(response.text))
        l.add_xpath('agent_name', self.agent_name_xpath)
        l.add_xpath('purpose', self.purpose_xpath, re='Property (.+)')
        l.add_xpath('property_type', self.property_type_xpath)

        l.add_xpath('area', self.area_xpath)
        l.add_xpath('area_unit', self.area_unit_xpath)
        l.add_xpath('bedroom', self.bedroom_xpath)
        l.add_xpath('ad_id', self.ad_id_xpath, re='\d+')

        l.add_value('date_on_website', self.date_on_website_re.findall(response.text), re='(.+)T')
        l.add_xpath('date_on_website', self.date_on_website_xpath)
        l.add_value('date_scraped', datetime.datetime.now().strftime("%Y-%m-%d"))
        l.add_value('product_url', response.url)
        l.add_xpath('agent_url', self.agent_url_xpath, lambda v: urljoin(response.url, v[0]))

        yield l.load_item()

        if response.status in self.handle_httpstatus_list:
            error_item = ErrorItem()
            error_item['url'] = response.meta.get('_origin_url')
            error_item['reason_code'] = response.status
            error_item['table'] = 'listings'
            yield error_item

        response.meta['_phone_number'] = l.get_output_value('phone_number')

        agent_url = l.get_output_value('agent_url')
        if agent_url:
            yield response.request.replace(
                url=agent_url,
                meta=response.meta,
                callback=self.parse_agent_info
            )

    def parse_agent_info(self, response):
        l = OlxItemLoader(item=UserItem(), response=response)

        l.add_xpath('name', self.user_name_xpath)
        l.add_value('number_account', self.number_account_re.findall(response.url))
        l.add_xpath('verified_member', self.verified_number_xpath)
        l.add_xpath('since_date', self.since_date_xpath)
        l.add_value('user_date_scraped', datetime.datetime.now().strftime("%Y-%m-%d"))
        l.add_value('user_url', response.url)
        l.add_value('phone_number', response.meta.get('_phone_number'))

        if response.status in self.handle_httpstatus_list:
            error_item = ErrorItem()
            error_item['url'] = response.meta.get('_origin_url')
            error_item['reason_code'] = response.status
            error_item['table'] = 'users'
            yield error_item

        yield l.load_item()
