#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from .utils import get_config


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

    def make_request_dont_filter(self, url):
        return Request(url, dont_filter=True)
