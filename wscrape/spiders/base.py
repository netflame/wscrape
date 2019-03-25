#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from .utils import get_config, PRIORITY_TOP


class BaseSpider(RedisSpider):
    
    # config placeholder
    config = {}
    config_name = ''

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):

        def init_config():
            if self.config:
                return
            self.config = get_config(self.config_name)

        obj = super().from_crawler(crawler, *args, **kwargs)
        init_config()
        return obj

    def make_base_request(self, url):
        return Request(url, dont_filter=True, priority=PRIORITY_TOP+1)
    
    def errback(self, failure):
        self.logger.error(repr(failure))
