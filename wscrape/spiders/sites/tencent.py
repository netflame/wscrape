# -*- coding: utf-8 -*-

import json
import re
import scrapy
from scrapy.http import Request
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.base import BaseSpider
from wscrape.spiders.utils import get_priority

__all__ = ['TencentSpider']

class TencentSpider(BaseSpider):
    name = 'tencent'
    allowed_domains = ['qq.com']

    ext = ''
    num = 20
    
    # overwrite config name
    config_name = 'tencent'

    def start_requests(self):
        if not self.ext:
            start_urls = [
                self.config['article']['list'] % {'ext': ext, 'page': 0, 'num': self.num} for ext in self.config['ext']
            ]
        else:
            start_urls = [
                self.config['article']['list'] % {'ext': self.ext, 'page': 0, 'num': self.num}
            ]
        for url in start_urls:
            yield self.make_base_request(url)
        
    def parse(self, response):
        text = response.text
        data = json.loads(text).get('data')

        # datanum 字段也可用
        if not data:
          return  

        for d in data:
            article = NewsDetailItem()
            article['id'] = d['id']
            article['category'] = d['category']
            article['source'] = 'tencent'

            article['title'] = d['title']
            article['abstract'] = d['intro']

            article['url'] = d['vurl']
            article['genre'] = d['article_type']
            article['publish_time'] = d['ts']  # utils.get_ts(d['publish_time'])

            article['comments_id'] = d['comment_id']
            # article['comments_id'] = article['id']
            article['comments_count'] = d['comment_num']

            author = Author()
            author['id'] = d['source_id']
            author['name'] = d['source']
            author['url'] = self.config['author'] % {'author_id': author['id']}
            article['author'] = author

            article['keywords'] = d['keywords']
            article['tags'] = d['tags']
            article['view_count'] = d['view_count']

            priority = get_priority(comments_count=article['comments_count'], view_count=article['view_count'])
            meta = {'article': article, 'priority': priority}
            if d.get('from', '') == 'kuaibao':                      # 快报 -> 主要为 ent 信息
                yield Request(self.config['kuaibao'] % {'id': d['app_id']}, callback=self.parse_article, priority=priority, meta=meta)
            else:
                yield Request(article['url'], callback=self.parse_article, priority=priority, meta=meta)
        page = re.sub(r'.*?page=(?P<page>\d+).*', r'\g<page>', response.request.url)
        request_url = response.request.url.replace('page=%s' % page, 'page=%d' % (int(page)+1))
        yield self.make_base_request(request_url)


    def parse_article(self, response):
        article = response.meta['article']
        p = 'p.text::text'      # > 快报->p.text.textNode
        article['content'] = '\n'.join(p.strip() for p in response.css(p).extract())
        yield article

        comment_id = article['comments_id']
        comment_url = self.config['article']['comment'] % {'comment_id': comment_id, 'last': 0, 'reqnum': self.num}
        
        comments = Comments()
        comments['id'] = article['comments_id']
        comments['url'] = comment_url
        comments['count'] = article['comments_count']
        comments['comments'] = []
        yield comments

        priority = response.meta['priority']
        meta = {'comments_id': comments['id'], 'priority': priority}
        yield Request(comment_url, callback=self.parse_comment, priority=priority, meta=meta)

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
            user['gender'] = duser['gender']

            comment['user'] = user
            yield comment

        if data['hasnext']:
            last = data['last']
            next_comment_url = re.sub(r'commentid=\w+?&', 'commentid=%s&' % last, response.request.url, 1)
            yield Request(next_comment_url, callback=self.parse_comment, priority=response.meta['priority'], meta=response.meta)
