# -*- coding: utf-8 -*-

from ..sites import (
    NeteaseSpider,
    SohuSpider,
    TencentSpider,
    ToutiaoSpider,
)


class WorldTencentSpider(TencentSpider):
    name = 'world_tencent'
    ext = 'world'


class WorldNeteaseSpider(NeteaseSpider):
    name = 'world_netease'
    category = 'world'
    # category = "temp"
    # data_location = "cm_guoji"


class WorldToutiaoSpider(ToutiaoSpider):
    name = 'world_toutiao'
    category = 'world'


class WorldSohuSpider(SohuSpider):
    name = 'world_sohu'
    category = "world"
