# -*- coding: utf-8 -*-

from ..sites import (
    NeteaseSpider,
    SohuSpider,
    TencentSpider,
    ToutiaoSpider,
)


class TechTencentSpider(TencentSpider):
    name = 'tech_tencent'
    ext = 'tech'


class TechNeteaseSpider(NeteaseSpider):
    name = 'tech_netease'
    category = "tech"
    # data_location = "tech_datalist"

    # 滚动新闻："http://tech.163.com/special/gd2016/"


class TechToutiaoSpider(ToutiaoSpider):
    name = 'tech_toutiao'
    category = 'tech'


class TechSohuSpider(SohuSpider):
    name = 'tech_sohu'
    category = "tech"
