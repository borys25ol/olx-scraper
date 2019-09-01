from scrapy.conf import settings
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, DateTime, Text


DeclarativeBase = declarative_base()


def db_connect_to_listings():
    return create_engine(settings.get("LISTINGS_CONNECTION_STRING"))


def db_connect_to_users():
    return create_engine(settings.get("USERS_CONNECTION_STRING"))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class ListingDB(DeclarativeBase):
    __tablename__ = "LISTINGS"

    id = Column(Integer, primary_key=True)

    breadcrumb = Column('breadcrumb', String(250))
    featured = Column('featured', String(250))
    images_count = Column('images_count', Integer())
    images_urls = Column('images_urls', Text())
    description = Column('description', Text())
    price = Column('price', String(250))
    title = Column('title', String(250))
    location = Column('location', String(250))
    city = Column('city', String(250))
    province = Column('province', String(250))
    phone = Column('phone', String(250))
    agent_name = Column('agent_name', String(250))
    property_type = Column('property_type', String(250))
    purpose = Column('purpose', String(250))
    area = Column('area', String(250))
    area_unit = Column('area_unit', String(250))
    bedroom = Column('bedroom', String(250))
    ad_id = Column('ad_id', Integer())
    date_on_website = Column('date_on_website', DateTime())
    date_scrapped = Column('date_scrapped', DateTime())
    user_url = Column('user_url', Text())
    product_url = Column('product_url', Text())


class UserDB(DeclarativeBase):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True)

    user_id = Column('user_id', Integer())
    user_name = Column('user_name', Text())
    phone_number = Column('phone_number', Text())
    verified = Column('verified', String(250))
    member_since = Column('member_since', String(250))
    date_scraped = Column('date_scraped', DateTime())
    user_url = Column('user_url', Text())
