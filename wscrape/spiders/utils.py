# -*- coding: utf-8 -*-

import re
import time
import toml
# from os.path import abspath, join, split
from pkgutil import get_data
from wscrape.spiders import __package__


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

def get_priority():
    pass


def show():
    print(__package__)