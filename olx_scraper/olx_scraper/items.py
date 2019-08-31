# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import replace_entities

from olx_pk_scraper.olx_scraper.olx_scraper.utils.extractors import clean_spaces, clean_text


class OlxItemLoader(ItemLoader):
    default_input_processor = MapCompose(
        clean_text,
        replace_entities,
        clean_spaces,
        str.strip,
    )
    default_output_processor = TakeFirst()

    purpose_in = MapCompose(default_input_processor, lambda v: v.title())
    breadcrumb_out = Join(separator='/')

    image_urls_in = MapCompose(default_input_processor)
    image_urls_out = Join(separator=', ')
    verified_member_out = Join(separator='|')


class OlxItem(scrapy.Item):
    breadcrumb = scrapy.Field(type=str)
    count_of_images = scrapy.Field()
    featured = scrapy.Field()
    image_urls = scrapy.Field(type=list)
    description = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    city = scrapy.Field()
    province = scrapy.Field()
    phone_number = scrapy.Field()
    agent_name = scrapy.Field()
    property_type = scrapy.Field()
    purpose = scrapy.Field()

    area = scrapy.Field()
    area_unit = scrapy.Field()
    bedroom = scrapy.Field()
    ad_id = scrapy.Field()
    date_on_website = scrapy.Field()
    date_scraped = scrapy.Field()

    user_name = scrapy.Field()
    number_account = scrapy.Field()
    verified_member = scrapy.Field()
    since_date = scrapy.Field()
    user_date_scraped = scrapy.Field()
    product_url = scrapy.Field()
    agent_url = scrapy.Field()
