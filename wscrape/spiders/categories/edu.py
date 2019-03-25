# -*- coding: utf-8 -*-

from wscrape.spiders.sites import *

class EduTencentSpider(TencentSpider):
    name = 'edu_tencent'
    ext = 'edu'


class EduNeteaseSpider(NeteaseSpider):
    name = 'edu_netease'
    category = 'edu'
    # data_location = "newsdata_edu_hot"


class EduToutiaoSpider(ToutiaoSpider):
    name = 'edu_toutiao'
    category = 'edu'


class EduSohuSpider(SohuSpider):
    name = 'edu_sohu'
    category = 'edu'
