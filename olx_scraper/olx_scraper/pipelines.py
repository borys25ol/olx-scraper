# -*- coding: utf-8 -*-
import datetime
import re

from olx_scraper.items import OlxItem, UserItem


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


class NormalizeDatePipeline(object):

    date_on_page_re = re.compile('(\d+) days ago')

    def process_item(self, item, spider):
        if isinstance(item, OlxItem):
            date = item.get('date_on_website')
        elif isinstance(item, UserItem):
            date = item.get('since_date')
        else:
            date = None
        if date:
            if 'ago' in date:
                time_delta = self.date_on_page_re.findall(date)
                time_delta = int(time_delta[0]) if time_delta else None
            elif 'Today' in date:
                time_delta = 0
            elif 'Yesterday' in date:
                time_delta = 1
            else:
                time_delta = None

            if time_delta:
                today_date = datetime.date.today()
                normalize_date = today_date - datetime.timedelta(days=time_delta)
                if isinstance(item, UserItem):
                    item['since_date'] = normalize_date.strftime("%Y-%m")
                elif isinstance(item, OlxItem):
                    item['date_on_website'] = normalize_date.strftime("%Y-%m-%d")

            else:
                if isinstance(item, UserItem):
                    datetime_obj = datetime.datetime.strptime(date, '%b %Y')
                    item['since_date'] = datetime.datetime.strftime(datetime_obj, '%Y-%m')
                if isinstance(item, OlxItem):
                    datetime_obj = datetime.datetime.strptime(date, '%b %d')

                    today = datetime.datetime.today()
                    item_date = datetime_obj.replace(year=2019)
                    if item_date > today:
                        date = datetime.datetime.strftime(item_date.replace(year=2018), "%Y-%m-%d")
                    else:
                        date = datetime.datetime.strftime(datetime_obj.replace(year=2019), "%Y-%m-%d")

                    item['date_on_website'] = date

        return item
