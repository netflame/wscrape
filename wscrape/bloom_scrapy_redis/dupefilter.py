#!/usr/bin/env python
# -*- coding: utf-8 -*-


from scrapy_redis.dupefilter import RFPDupeFilter
from . import defaults
from .utils import SeedUtil


class BloomFilter(RFPDupeFilter):
    """
        误判率 f 最低时，有
            k = (m/n)*ln2 ≈ 0.7*m/n

            ----------> m ≈ 1.4*k*n
        其中
            k: 不同hash函数的格式
            m: 位数组的长度
            n: 待判断的集合元素个数
        
        比如 n 有 10万 个元素，
            对于RFP: 10^5*160 = 2B*10^6 = 2MB 
            对于 BF: 取 k=8，则 m ≈ 10^6bit ≈ 2^20bit ＝ 1/8 MB
    """

    # place holder
    bf_bits = 0
    bf_seeds = 0

    # this won't work
    # @classmethod
    # def from_settings(cls, settings):
        # obj = super().from_settings(settings)
        # obj.update_from_setting(settings)
        # return obj

    # this will work in scheduler->open
    def update_from_settings(self, settings):
        self.bf_bits = settings.getint("BLOOM_FILTER_BITS", defaults.BLOOM_FILTER_BITS)
        if self.bf_bits < 1:
            raise ValueError("Bit num for Bloom Filter must be greater than 1")

        self.bf_seeds = settings.getlist("BLOOM_FILTER_SEEDS", defaults.BLOOM_FILTER_SEEDS)
        if not self.bf_seeds:
            self.bf_k = settings.getint("BLOOM_FILTER_K", defaults.BLOOM_FILTER_K)
            self.bf_seeds = SeedUtil.generate_seeds(self.bf_k)
        
        self.bf_check_bits = settings.get("BLOOM_FILTER_CHECK_BITS", defaults.BLOOM_FILTER_CHECK_BITS)

        self.bf_m = 1 << self.bf_bits
        self.bf_check_key = settings.get("BLOOM_FILTER_CHECK_KEY", defaults.BLOOM_FILTER_CHECK_KEY) % {'sdk': self.key}
        self.bf_check_m = 1 << self.bf_check_bits

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if not self.exists(fp):
            self.insert(fp)
            return False
        return True

    def log(self, request, spider):
        super().log(request, spider)
        spider.crawler.stats.inc_value('dupefilter/filtered', spider=spider)

    def exists(self, value):
        flags = self.mget(value)
        for flag in flags:
            if not flag:
                return False
        return True

    def insert(self, value):
        self.mset(value)

    def mget(self, value):
        offsets = self.get_offsets(value)
        check_offset = self.get_check_offset(offsets)
        with self.server.pipeline(transaction=False) as p:
            for offset in offsets:
                p.getbit(self.key, offset)
            p.getbit(self.bf_check_key, check_offset)
            return p.execute()

    def mset(self, value):
        offsets = self.get_offsets(value)
        check_offset = self.get_check_offset(offsets)
        with self.server.pipeline(transaction=False) as p:
            for offset in offsets:
                p.setbit(self.key, offset, 1)
            p.setbit(self.bf_check_key, check_offset, 1)
            p.execute()

    def get_offsets(self, value):
        return [self.hash(value, seed) for seed in self.bf_seeds]

    def get_check_offset(self, offsets):
        """ 记录 k 个 offset 置入的顺序，作为第二重校验
        
        Parameters
        ----------
        offsets: str
            k 个有序的 offset （有序指置入顺序）
        """
        offsets_str = "".join(map(str, offsets))
        return self.hash_check(offsets_str)

    def hash(self, value, seed):
        h = 0
        for i in range(len(value)):
            h += seed * h + ord(value[i])
        h &= self.bf_m - 1
        return h

    def hash_check(self, value):
        """
        类似bitmap
        """
        return int(value) % self.bf_check_m
