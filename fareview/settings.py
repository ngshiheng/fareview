import os

BOT_NAME = 'fareview'

SPIDER_MODULES = ['fareview.spiders']
NEWSPIDER_MODULE = 'fareview.spiders'

# Scraper API
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# scrapy-fake-useragent
# https://github.com/alecxe/scrapy-fake-useragent
FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # This is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # If FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # Fall back to USER_AGENT value
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = os.environ.get('ROBOTSTXT_OBEY', True)

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5 if SCRAPER_API_KEY is not None else 16
RETRY_TIMES = os.environ.get('RETRY_TIMES', 10)

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0 if SCRAPER_API_KEY is not None else 2
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
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'fareview.middlewares.FareviewSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'fareview.extensions.SentryLogging': -1,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'fareview.pipelines.FareviewPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = os.environ.get('HTTPCACHE_EXPIRATION_SECS', 0)
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Sentry
# https://stackoverflow.com/questions/25262765/handle-all-exception-in-scrapy-with-sentry
SENTRY_DSN = 'https://fa2a66ed7b8e4702b9c405f29a8b5df8@o545253.ingest.sentry.io/5704972'

# PostgreSQL
DATABASE_CONNECTION_STRING = '{drivername}://{user}:{password}@{host}:{port}/{db_name}'.format(
    drivername='postgresql',
    user=os.environ.get('PG_USERNAME', 'postgres'),
    password=os.environ.get('PG_PASSWORD'),
    host=os.environ.get('PG_HOST', 'localhost'),
    port=os.environ.get('PG_PORT', '5432'),
    db_name=os.environ.get('PG_DATABASE', 'fareview'),
)
