# -*- coding: utf-8 -*-

import re
import json
import scrapy
from json import JSONDecodeError
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.base import BaseSpider
from ..utils import get_ts

__all__ = ['NeteaseSpider']

class NeteaseSpider(BaseSpider):
    name = 'netease'
    allowed_domains = ['163.com']

    category = ''
    limit = 20

    # overwrite config name
    config_name = 'netease'

    def start_requests(self):
        # self.config = get_config('netease')
        if not self.category:
            start_urls = [
                self.config['article']['list'] % {'feed_id': feed_id, 'offset': 0, 'limit': self.limit} for feed_id in self.config['feed'].values()
            ]
        else:
            start_urls = [
                self.config['article']['list'] % {'feed_id': self.config['feed'].get(self.category), 'offset': 0, 'limit': self.limit},
            ]
        for url in start_urls:
            yield self.make_request_dont_filter(url)
    
    def parse(self, response):
        text = response.text
        if not text:
            return
        r = re.search(r"artiList\(\{\"(.*?)\":(.*)\}\)", text, re.S)
        if not r:
            return

        category = self._get_category(r.group(1))

        try:
            data = json.loads(r.group(2))

            if not data:
                return

            for d in data:
                url = d['url']
                if d['docid'] not in url:   # 忽略该类url
                    continue

                item = NewsDetailItem()
                item['id'] = d['docid']
                item['category'] = category
                item['source'] = 'netease'
            
                item['title'] = d['title']
                item['abstract'] = d['digest']

                item['url'] = d['url']
                # item['genre']
                item['publish_time'] = get_ts(d['ptime'])
                # item['behot_time']

                item['comments_count'] = d['commentCount']
                item['comments_id'] = item['id']

                author = Author()
                author['name'] = d['source']
                item['author'] = author

                yield Request(item['url'], callback=self.parse_article, meta={'item': item})
        except JSONDecodeError:
            # 描述或者title中有双引号
            pass

        r = re.search(r'(\d+)-(\d+)\.html$', response.request.url)
        if not r:   # 基本不会出现该情况，加上保险
            return
        offset, limit = int(r.group(1)), int(r.group(2))
        request_url = response.request.url.replace('%d-%d.html' % (offset, limit), '%d-%d.html' % (offset+limit, limit))
        yield self.make_request_dont_filter(request_url)

    # 采用传递item来一次yield item
    def parse_article(self, response):
        item = response.meta['item']

        item['genre'] = response.css('meta[property="og:type"]::attr("content")').extract_first()
        item['keywords'] = response.css('meta[name="keyword"]::attr("content")').extract_first()
        item['tags'] = response.css('meta[property="article:tag"]::attr("content")').extract_first()

        abstract = response.css('meta[property="og:description"]::attr("content")').extract_first()
        if not item['abstract']:
            item['abstract'] = abstract

        item['content'] = '\n'.join([p.strip() for p in response.css('div.page.js-page p::text').extract()])

        yield item

        comment_url = self.config['article']['comment'] % {'product_key': self.config['product_key'], 'article_id': item['id'], 'type': 'new', 'offset': 0, 'limit': self.limit}

        comments = Comments()
        comments['id'] = item['comments_id']
        comments['url'] = comment_url
        comments['count'] = item['comments_count']
        comments['comments'] = []
        yield comments

        yield Request(comment_url, callback=self.parse_comment, meta={'comments_id': comments['id']})

    # 不传递item，而是根据id更新item
    def parse_comment(self, response):
        comments_id = response.meta['comments_id']

        text = response.text
        data = json.loads(text).get('comments', '')
        if not data:
            return

        for id, d in data.items():
            comment = Comment()
            comment['id'] = id
            comment['content'] = d['content']
            comment['publish_time'] = get_ts(d['createTime'])
            comment['vote'] = d['vote']

            comment['comments_id'] = comments_id

            user, duser = User(), d['user']
            user['id'] = duser['userId']
            user['region'] = duser['location']
            user['name'] = duser.get('nickname', '')
            user['type_'] = duser.get('userType', '')

            comment['user'] = user
            yield comment

        r = re.search(r'offset=(\d+)&limit=(\d+)', response.url)
        if not r:
            return
        offset, limit = int(r.group(1)), int(r.group(2))
        request_url = response.url.replace("offset=%d" % offset, "offset=%d" % (offset+limit))
        yield Request(request_url, self.parse_comment, meta={'comments_id': comments_id})

    def _get_category(self, feed_id):
        for k, v in self.config['feed'].items():
            if feed_id == v:
                return k
        return "Unknown"