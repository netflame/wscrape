# -*- coding: utf-8 -*-

import re
import json
import scrapy
from json import JSONDecodeError
from scrapy.http import Request
from scrapy.utils.request import request_fingerprint
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.basespider import BaseSpider
from wscrape.spiders.utils import get_ts, get_priority

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
            request = self.make_base_request(url)
            self.whitelist.add(request_fingerprint(request))
            yield request
    
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

                article = NewsDetailItem()
                article['id'] = d['docid']
                article['category'] = category
                article['source'] = 'netease'
            
                article['title'] = d['title']
                article['abstract'] = d['digest']

                article['url'] = d['url']
                article['publish_time'] = get_ts(d['ptime'])

                article['comments_count'] = d['commentCount']
                article['comments_id'] = article['id']

                author = Author()
                author['name'] = d['source']
                article['author'] = author

                priority = get_priority(comments_count=article['comments_count'])
                meta = {'article': article, 'priority': priority}
                yield Request(article['url'], callback=self.parse_article, priority=priority, meta=meta)

                self._update_stats('netease', category, 'feed')
        except JSONDecodeError:
            # 描述或者title中有双引号
            pass

        r = re.search(r'(\d+)-(\d+)\.html$', response.request.url)
        if not r:   # 基本不会出现该情况，加上保险
            return
        offset, limit = int(r.group(1)), int(r.group(2))
        request_url = response.request.url.replace('%d-%d.html' % (offset, limit), '%d-%d.html' % (offset+limit, limit))
        base_request = self.make_base_request(request_url)
        self.whitelist.add(request_fingerprint(base_request))
        yield base_request

    # 采用传递item来一次yield item
    def parse_article(self, response):
        article = response.meta['article']

        article['genre'] = response.css('meta[property="og:type"]::attr("content")').extract_first()
        article['keywords'] = response.css('meta[name="keyword"]::attr("content")').extract_first()
        article['tags'] = response.css('meta[property="article:tag"]::attr("content")').extract_first()

        abstract = response.css('meta[property="og:description"]::attr("content")').extract_first()
        if not article['abstract']:
            article['abstract'] = abstract

        article['content'] = '\n'.join([p.strip() for p in response.css('div.page.js-page p::text').extract()])

        yield article
        
        self._update_stats('netease', article['category'], 'article')

        comment_url = self.config['article']['comment'] % {'product_key': self.config['product_key'], 'article_id': article['id'], 'type': 'new', 'offset': 0, 'limit': self.limit}

        comments = Comments()
        comments['id'] = article['comments_id']
        comments['url'] = comment_url
        comments['count'] = article['comments_count']
        comments['comments'] = []
        yield comments

        priority = response.meta['priority']
        meta = {'comments_id': comments['id'], 'priority': priority, 'category': article['category']}
        yield Request(comment_url, callback=self.parse_comment, priority=priority, meta=meta)

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
            user['id'] = duser['userId']                    # useId为0表示该用户是匿名用户
            user['region'] = duser['location']
            user['name'] = duser.get('nickname', '')
            user['type_'] = duser.get('userType', '')

            comment['user'] = user
            yield comment

            self._update_stats('netease', response.meta['category'], 'comment')

        r = re.search(r'offset=(\d+)&limit=(\d+)', response.url)
        if not r:
            return
        offset, limit = int(r.group(1)), int(r.group(2))
        request_url = response.url.replace("offset=%d" % offset, "offset=%d" % (offset+limit))
        priority = response.meta['priority']
        yield Request(request_url, self.parse_comment, priority=priority, meta=response.meta)

    def _get_category(self, feed_id):
        for k, v in self.config['feed'].items():
            if feed_id == v:
                return k
        return "Unknown"
