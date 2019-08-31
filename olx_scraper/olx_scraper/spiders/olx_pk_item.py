# -*- coding: utf-8 -*-
import re

import scrapy

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

    breadcrumb_xpath = '//ol/li/a'
    image_urls_xpath_1 = '//*[@id="container"]/main/div/div/div[4]/div/div/div[4]/div/div/div//button/@style'
    image_urls_xpath_2 = '//div[@class="slick-track"]//img/@src'
    count_of_images_xpath = '//div[contains(@class, "slick-slider")]/..//span'
    featured_xpath = '//span[contains(text(), "Featured")]'
    description_xpath = '//div[@data-aut-id="itemDescriptionContent"]'
    price_xpath = '//span[@data-aut-id="itemPrice"]'
    title_xpath = '//h1[@data-aut-id="itemTitle"]'
    location_xpath = '//h3[contains(text(), "Posted in")]/..//following-sibling::div/span'

    def parse(self, response):
        l = OlxItemLoader(item=OlxItem(), response=response)

        l.add_xpath('breadcrumb', self.breadcrumb_xpath)
        l.add_xpath('image_urls', self.image_urls_xpath_1, re=self.image_urls_re)
        if not l.get_output_value('image_urls'):
            l.add_xpath('image_urls', self.image_urls_xpath_2)
            l.add_value('count_of_images', '1')

        l.add_xpath('count_of_images', self.count_of_images_xpath, re=self.count_of_images_re)

        featured = l.get_xpath(self.featured_xpath)
        if featured:
            l.add_value('featured', 'yes')
        else:
            l.add_value('featured', 'no')

        l.add_xpath('description', self.description_xpath)
        l.add_xpath('price', self.price_xpath)
        l.add_xpath('title', self.title_xpath)

        l.add_xpath('location', self.location_xpath, re=self.location_re)
        l.add_xpath('city', self.location_xpath, re=self.city_re)
        l.add_xpath('province', self.location_xpath, re=self.province_re)

        return l.load_item()
