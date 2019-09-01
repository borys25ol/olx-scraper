# -*- coding: utf-8 -*-
import datetime
import re

from sqlalchemy.orm import sessionmaker

from olx_scraper.database.db import ListingDB, UserDB, db_connect_to_listings, db_connect_to_users, create_table
from olx_scraper.items import OlxItem, UserItem


class OlxScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class InvalidPurposePipeline(object):
    """Process item if purpose field contains not correct data.

    Correct data for 'purpose' -> ['rent', 'sale']

    Otherwise - skip item
    """
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
    """Process item if on the website there is image-mock (image not exist).

    Clear image_urls list and set count_of_images = 0;
    """
    def process_item(self, item, spider):
        if isinstance(item, OlxItem):
            images = item.get('image_urls')
            if 'statics.olx.com.pk' in images:
                item['image_urls'] = ''
                item['count_of_images'] = 0
        return item


class NormalizeDatePipeline(object):
    """Convert date from OLX to correct format.

    Examples:
        For Listing item:
            2 days ago -> 2019-08-30 (%Y-%m-%d)
            Today -> 2019-09-01
            Yesterday -> 2019-08-31
        For User item:
            Sep 2018 -> 2018-09
    """
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


class MySQLPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine_listings = db_connect_to_listings()
        engine_users = db_connect_to_users()
        create_table(engine_listings)
        create_table(engine_users)
        self.SessionListings = sessionmaker(bind=engine_listings)
        self.SessionUser = sessionmaker(bind=engine_users)

    @staticmethod
    def process_data(session, db):
        try:
            session.add(db)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def process_item(self, item, spider):
        """Save deals in the database.

        This method is called for every item pipeline component.
        """
        session_listings = self.SessionListings()
        session_users = self.SessionUser()
        listingdb = ListingDB()
        usersdb = UserDB()

        if isinstance(item, OlxItem):
            listingdb.breadcrumb = item.get('breadcrumb')
            listingdb.featured = item.get('featured')
            listingdb.images_count = item.get('count_of_images')
            listingdb.images_urls = item.get('image_urls')
            listingdb.description = item.get('description')
            listingdb.price = item.get('price')
            listingdb.title = item.get('title')
            listingdb.location = item.get('location')
            listingdb.city = item.get('city')
            listingdb.province = item.get('province')
            listingdb.phone = item.get('phone_number')
            listingdb.agent_name = item.get('agent_name')
            listingdb.property_type = item.get('property_type')
            listingdb.purpose = item.get('purpose')
            listingdb.area = item.get('area')
            listingdb.area_unit = item.get('area_unit')
            listingdb.bedroom = item.get('bedroom')
            listingdb.ad_id = item.get('ad_id')
            listingdb.date_on_website = item.get('date_on_website')
            listingdb.date_scrapped = item.get('date_scrapped')
            listingdb.user_url = item.get('agent_url')
            listingdb.product_url = item.get('product_url')

            self.process_data(session_listings, listingdb)

        if isinstance(item, UserItem):
            usersdb.user_id = item.get('number_account')
            usersdb.user_name = item.get('name')
            usersdb.phone_number = item.get('phone_number')
            usersdb.verified = item.get('verified_member')
            usersdb.member_since = item.get('since_date')
            usersdb.date_scraped = item.get('user_date_scrapped')
            usersdb.user_url = item.get('user_url')

            self.process_data(session_users, usersdb)

        return item