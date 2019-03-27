#!/usr/bin/env python
# -*- coding: utf-8 -*-

# the bit num of m
# m is the size of bit array for bloom filter
BLOOM_FILTER_BITS = 20

# k is the num of hash func which generates offset for a given value 
BLOOM_FILTER_K = 8

# the seed for hash func for generating diffrent offset
BLOOM_FILTER_SEEDS = [2, 3, 5, 7, 11, 13, 15, 17]

# the second key for check the inserted order of offset
BLOOM_FILTER_CHECK_KEY = '%(sdk)s:bfcheck'

# allowable max spider idle times when redis queue is empty, otherwise close spider
SPIDER_IDLE_MAX_TIMES = 360    # 360*5s/60s=30min