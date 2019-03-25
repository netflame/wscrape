# -*- coding: utf-8 -*-

from wscrape.spiders.sites import *


class EntTencentSpider(TencentSpider):
    name = 'ent_tencent'
    ext = 'ent'


class EntNeteaseSpider(NeteaseSpider):
    name = 'ent_netease'
    category = "ent"
    # data_location = "newsdata_index"


class EntToutiaoSpider(ToutiaoSpider):
    name = 'ent_toutiao'
    category = 'ent'


class EntSohuSpider(SohuSpider):
    name = 'ent_sohu'
    category = "ent"
