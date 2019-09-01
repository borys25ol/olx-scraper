# -*- coding: utf-8 -*-
from olx_scraper.items import OlxItem


class OlxScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class InvalidPurposePipeline(object):

    def __init__(self):
        self.valid_purpose = ['rent', 'sale']

    def process_item(self, item, spider):
        if isinstance(item, OlxItem):
            purpose = item.get('purpose')
            if purpose:
                if 'sale' in purpose.lower() or 'rent' in purpose.lower():
                    return item
        else:
            return item


class HandleStaticImageUrlPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, OlxItem):
            images = item.get('image_urls')
            if 'statics.olx.com.pk' in images:
                item['image_urls'] = ''
                item['count_of_images'] = 0
        return item
