# -*- coding: utf-8 -*-

# Scrapy settings for wscrape project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'wscrapebot'

SPIDER_MODULES = ['wscrape.spiders']
NEWSPIDER_MODULE = 'wscrape.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'wscrape (+http://www.yourdomain.com)'

# UserAgent type for fake-useragent
# UA_TYPE = 'random'

# The backup useragent
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16
RANDOMIZE_DOWNLOAD_DELAY = True

# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 60   # 1 min

# specifies a number of seconds. 
# If the spider remains open for more than that number of second, 
# it will be automatically closed with the reason closespider_timeout. 
# If zero (or non set), spiders won’t be closed by timeout.
# CLOSESPIDER_TIMEOUT = 1800   # 30mins

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# enable DNS in-memory cache
DNSCACHE_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}


# http proxy
HTTPPROXY_URL_RANDOM = "http://localhost:6001/random"
# HTTPPROXY_AUTH_ENCODING = "latin-1"

# stats collector
DOWNLOADER_STATS = True
RETRY_ENABLED = True
MMEUSAGE_ENABLED = True
DEPTH_STATS_VERBOSE = True
STATS_CLASS = 'scraprom.PromStatsCollector'

# SCRAPROM_PUSHGATEWAY_URL = '0.0.0.0:9091'
# SCRAPROM_JOB_NAME = ' scrapy'
# SCRAPROM_PUSH_TIMEOUT = 3
# SCRAPROM_UPDATE_INTERVAL = 5
# SCRAPROM_METRICS_PREFIX = 'scraprom'



# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    # 'wscrape.spidermiddlewares.SampleSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'wscrape.downloadermiddlewares.useragent.RandomUserAgentMiddleware': 500,
    'wscrape.downloadermiddlewares.httpproxy.RandomHttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'wscrape.pipelines.MongoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# ---------------- scrapy-splash ----------------------
# SPLASH_URL = 'localhost:8050'


# ----------------- scrapy-redis -----------------------
# Enables scheduling storing requests queue in redis.
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER = "wscrape.bloom_scrapy_redis.scheduler.BloomScheduler"

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "wscrape.bloom_scrapy_redis.dupefilter.BloomFilter"

# Settings for Bloom Filter
# BLOOM_FILTER_BITS = 20

# SEEDS's level is greater than K
# BLOOM_FILTER_SEEDS = [2, 3, 5, 7, 11, 13, 15, 17]
# BLOOM_FILTER_K = 8

# BLOOM_FILTER_CHECK_KEY = '%(sdk)s:bfcheck'  # sdk -> Scheduler Dupefilter Key

DUPEFILTER_DEBUG = True
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:bloomfilter'

# Default requests serializer is pickle, but it can be changed to any module
# with loads and dumps functions. Note that pickle is not compatible between
# python versions.
# Caveat: In python 3.x, the serializer must return strings keys and support
# bytes as values. Because of this reason the json or msgpack module will not
# work by default. In python 2.x there is no such issue and you can use
# 'json' or 'msgpack' as serializers.
#SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"

# Don't cleanup redis queues, allows to pause/resume crawls.
#SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# Alternative queues.
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
#SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Specify the host and port to use when connecting to Redis (optional).
#REDIS_HOST = 'localhost'
#REDIS_PORT = 6379

# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
#REDIS_URL = 'redis://user:pass@hostname:9001'
REDIS_URL = 'redis://localhost:6379'    # second `redis` is the service name

# Custom redis client parameters (i.e.: socket timeout, etc.)
#REDIS_PARAMS  = {}
# Use custom redis client class.
#REDIS_PARAMS['redis_cls'] = 'myproject.RedisClient'

# If True, it uses redis' ``SPOP`` operation. You have to use the ``SADD``
# command to add URLs to the redis queue. This could be useful if you
# want to avoid duplicates in your start urls list and the order of
# processing does not matter.
#REDIS_START_URLS_AS_SET = False

# Default start urls key for RedisSpider and RedisCrawlSpider.
#REDIS_START_URLS_KEY = '%(name)s:start_urls'

# Use other encoding than utf-8 for redis.
#REDIS_ENCODING = 'latin1'


# ----------------- mongodb ------------------------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "netflame"

# -------------- feed_export_encoding --------------
FEED_EXPORT_ENCODING = 'utf-8'