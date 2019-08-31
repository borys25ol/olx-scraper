# -*- coding: utf-8 -*-
import datetime
import re
from urllib.parse import urljoin

import scrapy
from scrapy.loader.processors import TakeFirst

from olx_scraper.items import OlxItemLoader, OlxItem


class OlxSpider(scrapy.Spider):
    name = 'olx.pk:item'

    allowed_domains = ['olx.com.pk']

    start_urls = ['https://www.olx.com.pk/item/3-bad-dd-rent-brand-new-flats-available-iid-1008636120']

    image_urls_re = re.compile('background-image:url\((.+)\)')
    count_of_images_re = re.compile('\d+\s+/\s+(\d+)')
    location_re = re.compile('(.+),.+,.+')
    city_re = re.compile('.+,(.+),.+')
    province_re = re.compile('.+,.+,(.+)')
    phone_number_re = re.compile('"key_name":"phone","value":"(\+\d+)"')
    date_on_website_re = re.compile('"created_at_first":"(.+?)"'
                                    )
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

    def parse(self, response):
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

        response.meta['_phone_number'] = l.get_output_value('phone_number')

        yield l.load_item()
