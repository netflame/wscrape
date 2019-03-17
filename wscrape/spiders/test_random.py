#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from scrapy import Spider
from scrapy.http import Request

class TestSpider(Spider):

    name = "test_random"

    def start_requests(self):
        for _ in range(2):
            yield Request("https://httpbin.org/ip", dont_filter=True)
    
    def parse(self, response):
        print(json.loads(response.text))