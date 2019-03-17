# -*- coding: utf-8 -*-

import json
import re
import scrapy
from scrapy.http import Request
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.base import BaseSpider
from ..utils import get_config

__all__ = ['TencentSpider']

class TencentSpider(BaseSpider):
    name = 'tencent'
    allowed_domains = ['qq.com']

    ext = ''
    num = 20
    
    # overwrite config name
    config_name = 'tencent'

    def start_requests(self):
        # self.config = get_config('tencent')
        if not self.ext:
            start_urls = [
                self.config['article']['list'] % {'ext': ext, 'page': 0, 'num': self.num} for ext in self.config['ext']
            ]
        else:
            start_urls = [
                self.config['article']['list'] % {'ext': self.ext, 'page': 0, 'num': self.num}
            ]
        for url in start_urls:
            yield self.make_request_dont_filter(url)
        
    def parse(self, response):
        text = response.text
        data = json.loads(text).get('data')

        # datanum 字段也可用
        if not data:
          return  

        for d in data:
            item = NewsDetailItem()
            item['id'] = d['id']
            item['category'] = d['category']
            item['source'] = 'tencent'

            item['title'] = d['title']
            item['abstract'] = d['intro']

            item['url'] = d['vurl']
            item['genre'] = d['article_type']
            item['publish_time'] = d['ts']  # d['publish_time']

            # item['comments_id'] = d['comment_id']
            item['comments_id'] = item['id']
            item['comments_count'] = d['comment_num']

            author = Author()
            author['id'] = d['source_id']
            author['name'] = d['source']
            author['url'] = self.config['author'] % {'author_id': author['id']}
            item['author'] = author

            item['keywords'] = d['keywords']
            item['tags'] = d['tags']
            item['view_count'] = d['view_count']

            if d.get('from', '') == 'kuaibao':
                yield Request(self.config['kuaibao'] % {'id': d['app_id']}, callback=self.parse_article, meta={'item': item, 'comment_id': d['comment_id'],'flag': 1})
            else:
                yield Request(item['url'], callback=self.parse_article, meta={'item': item, 'comment_id': d['comment_id']})
        page = re.sub(r'.*?page=(?P<page>\d+).*', r'\g<page>', response.request.url)
        request_url = response.request.url.replace('page=%s' % page, 'page=%d' % (int(page)+1))
        yield self.make_request_dont_filter(request_url)


    def parse_article(self, response):
        item = response.meta['item']
        p = 'p.text::text' if response.meta.get('flag', 0) else 'p.one-p::text'
        item['content'] = '\n'.join(p.strip() for p in response.css(p).extract())
        yield item

        # comment_id = item['comments_id']
        comment_id = response.meta['comment_id']
        comment_url = self.config['article']['comment'] % {'comment_id': comment_id, 'last': 0, 'reqnum': self.num}
        
        comments = Comments()
        # comments['id'] = comment_id
        comments['id'] = item['comments_id']
        comments['url'] = comment_url
        comments['count'] = item['comments_count']
        comments['comments'] = []
        yield comments

        yield Request(comment_url, callback=self.parse_comment, meta={'comments_id': comments['id']})

    def parse_comment(self, response):

        comments_id = response.meta['comments_id']

        text = response.text
        data = json.loads(text).get('data', None)
        if not (data and data.get('commentid', None)):
            return

        for d in data['commentid']:
            comment = Comment()
            comment['id'] = d['id']
            comment['content'] = d['content']
            comment['publish_time'] = d['time']
            comment['vote'] = d['up']

            comment['comments_id'] = comments_id

            user, duser = User(), d['userinfo']
            user['id'] = duser['userid']
            user['region'] = duser['region']
            user['name'] = duser['nick']

            comment['user'] = user
            yield comment

        if data['hasnext']:
            last = data['last']
            next_comment_url = re.sub(r'commentid=\w+?&', 'commentid=%s&' % last, response.request.url, 1)
            yield Request(next_comment_url, callback=self.parse_comment, meta={'comments_id': comments_id})
