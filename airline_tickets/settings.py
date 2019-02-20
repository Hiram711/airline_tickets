# -*- coding: utf-8 -*-

# Scrapy settings for airline_tickets project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'airline_tickets'

# DB Config
import os
import sys
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
META_DB_URI = os.environ.get('META_DB_URI') or prefix + os.path.join(basedir, 'data-dev.db')

# if using MongoPipeline then decomment this block
# MONGO_URI = 'mongodb://127.0.0.1:27017'
# MONGO_DB = 'airline_tickets'

# how many days after today the spider will crawl,if set thie option,the same option in the database will be override
CRAWLER_DAYS = 3

SPIDER_MODULES = ['airline_tickets.spiders']
NEWSPIDER_MODULE = 'airline_tickets.spiders'

## Selenium Config
# SELENIUM_TIMEOUT = 10
# SELENIUM_EXECUTABLE_PATH = r'D:\chromedriver_win32\chromedriver'
## Enable or disable downloader middlewares for Selenium
# DOWNLOADER_MIDDLEWARES = {
#     'airline_tickets.middlewares.RandomUserAgentMiddleware': 553,
#     'airline_tickets.middlewares.ProxyMiddleware': 554,
#     'airline_tickets.middlewares.SeleniumMiddleware': 555,
# }

# Splash Config
SPLASH_URL='http://10.42.1.74:8050'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DOWNLOADER_MIDDLEWARES = {
    'airline_tickets.middlewares.RandomUserAgentMiddleware': 553,
    'airline_tickets.middlewares.ProxyMiddleware': 554,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810
}
# Duplicate filter
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# Http Cache Storage
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Log config
from datetime import datetime
log_file_path = "log/%s.log"%datetime.now().strftime('%Y%m%d%H%M%S')
LOG_LEVEL = 'DEBUG'
LOG_FILE = log_file_path

# Enable this option to use proxy server
PROXY_URL = 'http://10.42.11.226:5010/get'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'airline_tickets.pipelines.SqlAlchemyPipeline': 300,
    # 'airline_tickets.pipelines.MongoPipeline': 301  # this pipeline is for MongoDB
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
