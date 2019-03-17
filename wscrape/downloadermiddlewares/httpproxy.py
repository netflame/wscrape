#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

class RandomHttpProxyMiddleware(HttpProxyMiddleware):

    def __init__(self, auth_encoding='latin-1', url_random="/random"):
        self.auth_encoding = auth_encoding
        self.url_random = url_random

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        url_random = crawler.settings.get("HTTPPROXY_URL_RANDOM", "http://localhost:6001/random")
        return cls(auth_encoding, url_random)

    def process_request(self, request, spider):
        request.meta['proxy'] = self._get_random_proxy()
        return super().process_request(request, spider)       # credentials related

    def _get_random_proxy(self):
        random_proxy = None
        try:
            r = requests.get(self.url_random)
            random_proxy = r.text
        except Exception:
            pass
        return random_proxy
