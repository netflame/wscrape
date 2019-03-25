# -*- coding: utf-8 -*-

import json
import re
import requests
import scrapy
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider
from wscrape.items import User, Author, Comment, Comments, NewsDetailItem
from wscrape.spiders.base import BaseSpider
from wscrape.spiders.utils import get_priority


__all__ = ['SohuSpider']

class SohuSpider(BaseSpider):
    name = 'sohu'
    allowed_domains = ['sohu.com']

    category = ""
    size = 20

    # overwrite config name
    config_name = 'sohu'

    def start_requests(self):
        # self.config = get_config('sohu')
        if not self.category:
            public_ = [self.config['feed'][category] for category in self.config['public']]
            public_urls = [
                self.config['article']['list']['public'] % {'scene': f['scene'], 'scene_id': f['scene_id'], 'page': 1, 'size': self.size} for f in public_
            ]
            integration_ = [self.config['feed'][category] for category in self.config['integration']]
            integration_urls = [
                self.config['article']['list']['integration'] % {'region': f['region'], 'page': 1, 'size': self.size} for f in integration_
            ]
            start_urls = public_urls + integration_urls
        else:
            if self.category in self.config['public']:
                ss = self.config['feed'][self.category]
                start_urls = [
                    self.config['article']['list']['public'] % {'scene': ss['scene'], 'scene_id': ss['scene_id'], 'page': 1, 'size': self.size}
                ]
            elif self.category in self.config['integration']:
                r = self.config['feed'][self.category]['region']
                start_urls = [
                    self.config['article']['list']['integration'] % {'region': r, 'page': 1, 'size': self.size}
                ]
            else:
                start_urls = []
            
        # page = 1
        # total_page = self.get_page_num(self.request_url)
        # for page in range(total_page):
            # url = self.request_url % page
            # yield scrapy.Request(url, callback=self.parse, errback=self.errback, meta={"page": page})
        
        for url in start_urls:
            yield self.make_base_request(url)

    def parse(self, response):
        resp = json.loads(response.text)
        if isinstance(resp, list):
            data = resp
        elif isinstance(resp, dict):
            data = resp['data']
        
        if 'public-api' in response.url:
            feed_id = re.sub(r'.*sceneId=(?P<feed_id>\d+).*', r'\g<feed_id>', response.url)
        elif 'integration-api' in response.url:
            feed_id = re.sub(r'.*region/(?P<feed_id>\d+).*', r'\g<feed_id>', response.url)
        else:
            feed_id = ''
        category = self._get_category(feed_id)
        
        # get pv
        article_ids = ','.join(map(str, [d['id'] for d in data]))
        pv_url = self.config['article']['pv'] % {'article_ids': article_ids}
        r = requests.get(pv_url)
        article_pvs = r.json() if r.status_code==200 else {}

        for d in data:
            # 跳过广告
            if "adps" in d:
                continue

            article = NewsDetailItem()
            article['id'] = d['id']
            article['category'] = category
            article['source'] = 'sohu'

            article['title'] = d['title']

            article['url'] = self.config['article']['url'] % {'article_id': d['id'], 'author_id': d['authorId']}
            article['genre'] = d['type']
            article['publish_time'] = d['publicTime'] // 1000

            article['view_count'] = article_pvs.get(str(article['id']), 0)

            article['comments_id'] = article['id']

            author = Author()
            author['id'] = d['authorId']
            author['name'] = d['authorName']
            author['url'] = self.config['author'] % {'author_id': author['id']}
            article['author'] = author

            article['tags'] = ';'.join([t['name'] for t in d['tags']]) if d.get('tags', None) else ''

            priority = get_priority(view_count=article['view_count'])
            meta = {'article': article, 'priority': priority}
            yield Request(article['url'], callback=self.parse_article, errback=self.errback, priority=priority, meta=meta)

        r = re.search(r'page=(\d+)', response.request.url)
        page = int(r.group(1))
        request_url = response.request.url.replace('page=%d' % page, 'page=%d' % (page+1))
        yield self.make_base_request(request_url)

    def parse_article(self, response):
        article = response.meta['article']

        article['abstract'] = response.css('meta[name="description"]::attr("content")').extract_first()
        article['keywords'] = response.css('meta[name="keywords"]::attr("content")').extract_first()
        article['content'] = '\n'.join(p.strip() for p in response.css('#articleContent p::text').extract())

        comment_url = self.config['article']['comment'] % {'article_id': article['id'], 'page': 1, 'size': self.size}
        r = requests.get(comment_url)
        comments_count = r.json()['data']['totalCount'] if r.status_code==200 else 0

        article['comments_count'] = comments_count
        yield article

        comments = Comments()
        comments['id'] = article['comments_id']
        comments['url'] = comment_url
        comments['count'] = comments_count
        comments['comments'] = []
        yield comments

        priority = response.meta['priority']
        meta = {'comments_id': comments['id'], 'priority': priority}
        yield Request(comment_url, callback=self.parse_comment, priority=response.meta['priority'], meta=meta)

    def parse_comment(self, response):

        data = json.loads(response.text).get('data', None)
        if not (data and data.get('comments', None)):
            return
        
        # 'participation' 该字段后续可用

        comments, users = data['comments'], data['users']
        # article_id = data['sourceId'].lstrip('mp_')
        comments_id = response.meta['comments_id']

        for d in comments:
            comment = Comment()
            comment['id'] = d['id']
            comment['content'] = d['content']
            comment['publish_time'] = d['date'] // 1000
            comment['vote'] = d['likeCount']

            comment['comments_id'] = comments_id

            user = User()
            user['id'] = d['userId']
            user['region'] = d['location']
            user['name'] = users[str(d['userId'])]['userName']

            comment['user'] = user
            yield comment

        r = re.search(r'page_no=(\d+)', response.request.url)
        page = int(r.group(1))
        request_url = response.request.url.replace('page_no=%d' % page, 'page_no=%d' % (page+1))
        yield Request(request_url, callback=self.parse_comment, priority=response.meta['priority'], meta=response.meta)
    

    def _get_category(self, feed_id):
        return self.config['category'].get(feed_id, "Unknown")

    @staticmethod
    def get_page_num(url, page=100):
        def get_resp(url, page):
            resp = requests.get(url.format(page=page))
            return resp

        def is_valid(resp):
            if resp.status_code != 200:
                return False
            r = json.loads(resp.text)
            return (isinstance(r, list) and r) or (isinstance(r, dict) and r.get("data", None)) or (isinstance(r.get('data', None), dict) and r['data'].get('comments', None))
        
        success_page, fail_page = -1, -1    # 避免出现当结果只有一页且page初始为0时，造成while死循环

        while fail_page - success_page != 1:
            resp = get_resp(url, page)
            if is_valid(resp):
                success_page = page
                page = success_page * 2
            else:
                fail_page = page
                page = (success_page + fail_page) // 2
        
        return success_page