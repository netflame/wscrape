#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import dupefilter
from . import scheduler
from . import spiders


BloomFilter = dupefilter.BloomFilter
BloomScheduler = scheduler.BloomScheduler

CloseableRedisSpider = spiders.CloseableRedisSpider
CloseableCrawlRedisSpider = spiders.CloseableRedisCrawlSpider

__all__ = (
    'BloomFilter',
    'BloomScheduler',
    'CloseableRedisSpider',
    'CloseableCrawlRedisSpider',
)
