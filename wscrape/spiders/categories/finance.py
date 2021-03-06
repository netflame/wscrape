# -*- coding: utf-8 -*-

from wscrape.spiders.sites import *


class FinanceTencentSpider(TencentSpider):
    name = 'finance_tencent'
    ext = 'finance'


class FinanceNeteaseSpider(NeteaseSpider):
    name = 'finance_netease'
    category = "finance"
    # data_location = "newsdata_idx_index"


class FinanceToutiaoSpider(ToutiaoSpider):
    name = 'finance_toutiao'
    category = 'finance'


class FinanceSohuSpider(SohuSpider):
    name = 'finance_sohu'
    category = "finance"
