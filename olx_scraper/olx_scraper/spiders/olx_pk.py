# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class OlxPkSpider(scrapy.Spider):
    name = 'olx.pk'

    allowed_domains = ['olx.com.pk']

    start_urls = [
        'https://www.olx.com.pk/property-for-rent_c3',
        'https://www.olx.com.pk/property-for-sale_c2'
    ]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        categories_urls = response.xpath('//ul[@data-aut-id="subcategories"]/li/ul/li/a')

        for url in categories_urls:
            yield response.follow(url=url, callback=self.parse_category)

    def parse_category(self, response):
        pass
