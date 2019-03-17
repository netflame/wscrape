#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy_redis.scheduler import Scheduler


class BloomScheduler(Scheduler):

    def open(self, spider):
        super().open(spider)
        self.df.update_from_settings(spider.settings)
