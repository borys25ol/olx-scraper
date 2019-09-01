# -*- coding: utf-8 -*-
import random
from itertools import cycle
from scrapy.exceptions import NotConfigured

from olx_scraper.proxy.proxies import set_proxy


class RandomUserAgentMiddleware(object):
    """For every request set random useragent from USERAGRNTS_LIST

    If USERAGENT_DEBUG = True, log current useragent to terminal
    """
    def __init__(self, useragents_list, random_enable, debug):
        self.useragents_list = useragents_list
        self.random_enable = random_enable
        self.debug = debug

    @classmethod
    def from_crawler(cls, crawler):
        useragents_list = crawler.settings.getlist('USERAGENTS_LIST', [])
        if not useragents_list:
            raise NotConfigured

        random.shuffle(useragents_list)
        useragents_list = cycle(useragents_list)

        random_enable = crawler.settings.get('RANDOM_USERAGENT', False)
        debug = crawler.settings.get('USERAGENT_DEBUG', False)
        return cls(useragents_list, random_enable, debug)

    def process_request(self, request, spider):
        ua = next(self.useragents_list)
        if ua:
            if self.random_enable:
                request.headers['User-Agent'] = ua
            if self.debug:
                spider.logger.debug(f'User-Agent "{ua}" used')


class RandomProxyMiddleware(object):
    """For every request set random proxy from free AWM proxy list

    Work only if PROXY_ENABLE = True
    """
    def __init__(self, proxies):
        self._proxies = cycle(proxies)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    @classmethod
    def from_settings(cls, settings):
        if not settings.get('PROXY_ENABLE'):
            raise NotConfigured('Proxy is disabled in settings')

        proxies = set(settings.get('PROXIES_LIST', []))

        proxies = list(proxies)
        if not proxies:
            raise NotConfigured('Proxies list are empty')

        random.shuffle(proxies)

        return cls(proxies)

    @property
    def proxy(self):
        return next(self._proxies)

    def process_request(self, request, spider):
        proxy = self.proxy
        spider.logger.debug(f'Proxy used: {proxy}')
        set_proxy(request, proxy)
