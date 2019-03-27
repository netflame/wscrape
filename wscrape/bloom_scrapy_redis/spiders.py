#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import defaults
from scrapy.exceptions import DontCloseSpider
from scrapy_redis.spiders import RedisMixin, RedisSpider, RedisCrawlSpider


class CloseableRedisMixin(RedisMixin):
    
    def setup_redis(self, crawler=None):
        # get allowable max idle times and init idle_times
        if crawler is None:
            crawler = getattr(self, 'crawler', None)
        if crawler is None:
            raise ValueError("crawler is required")
        # ensure we have a good crawler
        self.crawler = crawler
        self.idle_times = 0
        self.idle_max_times = crawler.settings.getint("SPIDER_IDLE_MAX_TIMES", defaults.SPIDER_IDLE_MAX_TIMES)
        super().setup_redis(crawler=crawler)
    
    def schedule_next_requests(self):
        """Schedules a request if available, then return True. else return False"""
        r = False
        for req in self.next_requests():
            r = True
            self.crawler.engine.crawl(req, spider=self)
        return r

    def spider_idle(self):
        """Schedules a request if available, otherwise incr idle_times, close spider when idle_times exceed SPIDER_IDLE_MAX_TIMES."""
        r = self.schedule_next_requests()
        self.idle_times += 1
        if r:
            self.idle_times = 0
        if self.idle_times < self.idle_max_times:
            raise DontCloseSpider
        else:   # 可读性
            self.crawler.engine.close_spider(self, 'idle_times exceed')


class CloseableRedisSpider(CloseableRedisMixin, RedisSpider):
    pass

class CloseableRedisCrawlSpider(CloseableRedisMixin, RedisCrawlSpider):
    pass