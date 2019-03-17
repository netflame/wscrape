#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SeedUtil:

    @staticmethod
    def generate_seeds(k):
        """
        生成 k 个种子
        """
        return SeedUtil._generate_k_prime(k)

    @staticmethod
    def _generate_k_prime(k):
        """
        生成 k 个质数
        """
        if k < 1:
            raise ValueError("k must be greater than 1")

        if k == 1:
            return [2]

        primes, n = [2, 3], 2
        next_p = primes[-1] + 2
        while n < k:
            for p in primes:
                if next_p % p == 0:
                    break
            else:
                n += 1
                primes.append(next_p)
            next_p += 2
        
        return primes
