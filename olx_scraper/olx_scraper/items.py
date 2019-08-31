# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import replace_entities

from olx_scraper.utils.extractors import clean_text, clean_spaces


def modify_image_size(values):
    spileted_url = values.split(';')
    if spileted_url:
        output_link = ';'.join([spileted_url[0], 's=1080x1080'])
        return output_link
    else:
        return values


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

    image_urls_in = MapCompose(default_input_processor, modify_image_size)
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


class UserItem(scrapy.Item):
    name = scrapy.Field()
    number_account = scrapy.Field()
    verified_member = scrapy.Field(type=list)
    since_date = scrapy.Field()
    user_date_scraped = scrapy.Field()
    user_url = scrapy.Field()
    phone_number = scrapy.Field()


class ErrorItem(scrapy.Item):
    url = scrapy.Field()
    reason_code = scrapy.Field()
    table = scrapy.Field()
