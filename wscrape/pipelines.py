# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
# from bson import ObjectId
from wscrape.items import Comment, Comments, NewsDetailItem


class UcrawlPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get("MONGO_URI"),
            mongo_db = crawler.settings.get("MONGO_DB", "db_demo")
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, NewsDetailItem):
            self.db['news'].insert_one(dict(item))
        elif isinstance(item, Comments):
            self.db['comments'].insert_one(dict(item))
        elif isinstance(item, Comment):
            self.db['comments'].update_one({'id': item['comments_id']}, {'$addToSet': {'comments': dict(item)}})
        return item
