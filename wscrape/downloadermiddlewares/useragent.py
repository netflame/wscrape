#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import defaults
from fake_useragent import UserAgent, FakeUserAgentError

class RandomUserAgentMiddleware:
    """This middleware supports random user-agent"""
    
    def __init__(self, ua_type='random', backup_useragent="wscrape"):
        try:
            self.ua = UserAgent()
        except (FakeUserAgentError, Exception):
            self.ua = None
        self.ua_type = ua_type
        self.backup_useragent = backup_useragent
    
    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings.get('UA_TYPE', defaults.USERAGENT_TYPE), crawler.settings.get('USER_AGENT', defaults.BACKUP_USERAGENT))
        return o

    def process_request(self, request, spider):
        def user_agent():
            return getattr(self.ua, self.ua_type, self.backup_useragent)
        request.headers.setdefault(b'User-Agent', user_agent())