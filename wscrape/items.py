# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# TODO：用户信息挖掘
class User(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

    type_ = scrapy.Field()
    region = scrapy.Field()


class Author(User):
    # 其他细节，关注人数，发稿数量，发稿类型，所在地区，关注他的人的类型等等
    pass


class Comment(scrapy.Field):
    id = scrapy.Field()
    user = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field()

    vote = scrapy.Field()

    comments_id = scrapy.Field()


class Comments(scrapy.Field):
    id = scrapy.Field()             # 主键，选用文章id
    url = scrapy.Field()            # comment 启始url
    count = scrapy.Field()          # 评论数量
    comments = scrapy.Field()       # 数组，元素为评论


class NewsFeedItem(scrapy.Item):
    id = scrapy.Field()             # 文章id
    category = scrapy.Field()       # 新闻种类
    source = scrapy.Field()         # 来源站点

    title = scrapy.Field()          # 文章标题
    abstract = scrapy.Field()       # 文章摘要

    url = scrapy.Field()            # 文章url
    genre = scrapy.Field()          # 文章类型   （可能被移除）
    publish_time = scrapy.Field()   # 发布时间
    behot_time = scrapy.Field()     # 上次更新时间 (可能被移除)
    
    # comments_count = scrapy.Field()  # 评论数目，作为冗余

    keywords = scrapy.Field()       # 优先使用keywords
    labels = scrapy.Field()
    tags = scrapy.Field()

    author = scrapy.Field()         # 文章作者

    view_count = scrapy.Field()     # 播放或则阅读量


class NewsDetailItem(NewsFeedItem):
    content = scrapy.Field()

    comments_id = scrapy.Field()    # 选用文章id
    comments_count = scrapy.Field() # 评论数目