# -*- coding: utf-8 -*-
from olx_scraper.headers.useragents import USERAGENTS_LIST
from olx_scraper.proxy.proxies import PROXIES_LIST


BOT_NAME = 'olx_scraper'

SPIDER_MODULES = ['olx_scraper.spiders']
NEWSPIDER_MODULE = 'olx_scraper.spiders'

ROBOTSTXT_OBEY = False

USERAGENTS_LIST = USERAGENTS_LIST
USER_AGENT = USERAGENTS_LIST[0]
USERAGENT_DEBUG = True
RANDOM_USERAGENT = True

CONCURRENT_REQUESTS = 32

PROXY_ENABLE = False
PROXIES_LIST = PROXIES_LIST

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'From': 'googlebot(at)googlebot.com',
    'Connection': 'close'
}

#SPIDER_MIDDLEWARES = {
#    'olx_scraper.middlewares.OlxScraperSpiderMiddleware': 543,
#}

DOWNLOADER_MIDDLEWARES = {
   'olx_scraper.middlewares.RandomUserAgentMiddleware': 543,
   'olx_scraper.middlewares.RandomProxyMiddleware': 550,
}

#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

ITEM_PIPELINES = {
   'olx_scraper.pipelines.InvalidPurposePipeline': 300,
   'olx_scraper.pipelines.HandleStaticImageUrlPipeline': 320,
   # 'olx_scraper.pipelines.NormalizeDatePipeline': 320,
   # 'scrapy_project.pipelines.CsvPipeline': 350,
   # 'scrapy_project.pipelines.MySQLPipeline': 380,
}

AUTOTHROTTLE_ENABLED = False

LISTINGS_CONNECTION_STRING = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8".format(
    drivername="mysql",
    user="root",
    passwd="root",
    host="localhost",
    port="3306",
    db_name="LISTINGS",
)

USERS_CONNECTION_STRING = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8".format(
    drivername="mysql",
    user="root",
    passwd="root",
    host="localhost",
    port="3306",
    db_name="USERS",
)