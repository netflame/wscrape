# -*- coding: utf-8 -*-

import re
import time
import toml
# from os.path import abspath, join, split
from pkgutil import get_data
from wscrape.spiders import __package__

# used by scrapy.http.Request
PRIORITY_TOP = 1000
PRIORITY_UNIT = 100

def get_config(name=None, file='config.toml'):
    # config_path = join(split(abspath(__file__))[0], file)
    # config = toml.load(config_path)
    config_data = get_data(__package__, file).decode('utf-8')
    config = toml.loads(config_data)
    if name is None:
        return config
    return config.get(name, None)

def get_ts(str_time):
    # 先加个判断
    ts = 0
    if re.match(r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', str_time):
        f = '%Y-%m-%d %H:%M:%S'
        ta = time.strptime(str_time, f)
        ts = int(time.mktime(ta))   # in seconds
    return ts

def get_priority(comments_count=None, view_count=None):
        """
        以 PRIORITY_UNIT 为一个单元， priority 最高不超过 PRIORITY_TOP
        comments_count、view_count 权重比定为 2:8
        """
        base = 10
        if comments_count is None:
            comments_count, base = 0, 8
        if view_count is None:
            view_count, base = 0, 2
        priority = (comments_count * 2 + view_count * 8) // base // PRIORITY_UNIT
        return min(priority, PRIORITY_TOP)

def show():
    print(__package__)