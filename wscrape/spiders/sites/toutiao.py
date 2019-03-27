# -*- coding: utf-8 -*-

import json
import re
import scrapy
# import time
# from hashlib import md5
# from math import floor
# from selenium import webdriver
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.base import BaseSpider
from wscrape.spiders.utils import get_priority

__all__ = ['ToutiaoSpider']

class ToutiaoSpider(BaseSpider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    
    category = ""
    count = 20  # for comments

    # overwrite config name
    config_name = 'toutiao'

    def start_requests(self):
        self.cat_to_tag = dict(zip(self.config['categories'], self.config['tags']))
        self.tag_to_cat = dict(zip(self.config['tags'], self.config['categories']))

        as_, cp = self._get_as_cp()
        if not self.category:
            start_urls = [
                self.config['article']['list'] % {'tag': tag, 'as': as_, 'cp': cp, 'mbt': 0} for tag in self.config['tags']
            ]
        else:
            start_urls = [
                self.config['article']['list'] % {'tag': self.cat_to_tag[self.category], 'as': as_, 'cp': cp, 'mbt': 0}
            ]

        for url in start_urls:
            yield self.make_base_request(url)

    def parse(self, response):
        resp = json.loads(response.text)
        category = self.tag_to_cat.get(resp['page_id'].strip('/'), "Unknown")

        data = resp['data']
        # next_max_behot_time = resp['next']['max_behot_time']
        for d in data:
            # 跳过广告
            if 'ad_id' in d:
                continue
            
            article = NewsDetailItem()
            article['id'] = d['item_id']
            article['category'] = category
            article['source'] = 'toutiao'

            article['title'] = d['title']
            article['abstract'] = d.get('abstract', "")

            article['url'] = self.config['article']['url'] % {'article_id': article['id']}
            article['genre'] = d['article_type']
            article['publish_time'] = d['publish_time']  # 时间戳, 秒级，可用
            # article['behot_time'] = d['behot_time']

            article['comments_id'] = article['id']
            article['comments_count'] = d['comment_count']

            author = Author()
            author['id'] = d['media_info']['media_id'] if 'media_info' in d else "NO_ID"
            author['name'] = d['media_info']['name'] if 'media_info' in d else d.get('media_name', 'NO_NAME')
            author['url'] = self.config['user'] % {'user_id': author['id']}
            article['author'] = author

            article['keywords'] = d.get('keywords', "")
            # article['tags'] = d.get('tag', "")
            # article['labels'] = d.get('label', "")

            priority = get_priority(comments_count=article['comments_count'])
            meta = {'article': article, 'priority': priority}
            yield Request(article['url'], callback=self.parse_article, errback=self.errback, priority=priority, meta=meta)

        as_, cp = self._get_as_cp()
        mbt = data[-1]['behot_time']
        request_url = re.sub(r'as=.*?&cp=.*?&max_behot_time=\d+$', 'as=%s&cp=%s&max_behot_time=%d' % (as_, cp, mbt), response.request.url)
        # yield Request(request_url, callback=self.parse, errback=self.errback, priority=PRIORITY_TOP+1)
        yield self.make_base_request(request_url)

    def parse_article(self, response):
        article = response.meta['article']

        text = response.text
        article['keywords'] = response.css('meta[name="keywords"]::attr("content")').extract_first()
        abstract = response.css('meta[name="description"]::attr("content")').extract_first()
        if not article['abstract']:
            article['abstract'] = abstract

        r = re.search(r'tags:\s+(.*),', text)
        article['tags'] = ';'.join(dic.get('name','') for dic in json.loads(r.group(1))) if r else ''
        article['content'] = re.sub(r'.*?articleInfo.*?content:\s+\'(?P<content>.*?)\'.*', r'\g<content>', text, flags=re.S)

        comment_info = re.search(r'commentInfo.*?groupId:\s+\'(\d+).*?itemId:\s+\'(\d+).*?comments_count:\s+(\d+).*?ban_comment:\s+(\d+)', text, re.S)
        if comment_info:
            group_id, item_id, comment_count = [comment_info.group(i) for i in range(1, 4)]
            article['comments_count'] = comment_count
        else:
            group_id = item_id = article['id']

        yield article

        comment_url = self.config['article']['comment'] % {'group_id': group_id, 'item_id': item_id, 'offset': 0, 'count': self.count}
        
        comments = Comments()
        comments['id'] = article['comments_id']
        comments['url'] = comment_url
        comments['count'] = article['comments_count']
        comments['comments'] = []

        priority = response.meta['priority']
        meta = {'comments_id': comments['id'], 'priority': priority}
        yield Request(comment_url, callback=self.parse_comment, errback=self.errback, priority=priority, meta=meta)

    def parse_comment(self, response):
        data = json.loads(response.text).get('data', '')
        if not (data and data.get('comments', '')):
            return

        comments_id = response.meta['comments_id']

        for d in data['comments']:
            comment = Comment()
            comment['id'] = d['id']
            comment['content'] = d['text']
            comment['publish_time'] = d['create_time']
            comment['vote'] = d['digg_count']

            comment['comments_id'] = comments_id

            user, duser = User(), d['user']
            user['id'] = duser['user_id']
            user['name'] = duser['name']
            user['url'] = self.config['user'] % {'user_id': user['id']}
            comment['user'] = user

            yield comment

        offset = int(re.sub(r'.*offset=(?P<offset>\d+).*', r'\g<offset>', response.url))
        request_url = response.url.replace('offset=%d' % offset, 'offset=%d' % (offset+self.count))
        yield Request(request_url, callback=self.parse_comment, errback=self.errback, priority=response.meta['priority'], meta={'comments_id': comments_id})

    @staticmethod
    def _get_as_cp():
        return "479BB4B7254C150", "7E0AC8874BB0985"
        """
        t = floor(time.time())
        # e = "%X" % t
        e = hex(t)[2:].upper()
        i = md5(str(t).encode("utf-8")).hexdigest().upper()
        if len(e) != 8:
            return "479BB4B7254C150", "7E0AC8874BB0985"
        n, a, s, r = i[:5], i[-5:], "", ""
        for o in range(5):
            s += n[o] + e[0]
            r += e[o+3] + a[o]
        as_, cp = "A1%s%s" % (s, e[-3:]), "%s%sE1" % (e[:3], r)
        return as_, c
        """
