# Scrapy settings for website_scraper 
BOT_NAME                        = 'scraper'

SPIDER_MODULES                  = ['scraper.spiders']

# Obey robots.txt rules
ROBOTSTXT_OBEY                  = True

# Configure user agent
USER_AGENT                      = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configure delays for requests
DOWNLOAD_DELAY                  = 1
RANDOMIZE_DOWNLOAD_DELAY        = 0.5

# Configure concurrent requests
CONCURRENT_REQUESTS             = 8
CONCURRENT_REQUESTS_PER_DOMAIN  = 4

# Configure depth limit
DEPTH_LIMIT                     = 100
DEPTH_PRIORITY                  = 1

# Configure logging
LOG_LEVEL                       = 'DEBUG'

# Configure item pipelines
ITEM_PIPELINES                  = {'scraper.pipelines.WebsiteScraperPipeline': 300}

# Configure extensions
EXTENSIONS                      = {'scrapy.extensions.telnet.TelnetConsole' : None}

# Configure autothrottling
AUTOTHROTTLE_ENABLED            = True
AUTOTHROTTLE_START_DELAY        = 1
AUTOTHROTTLE_MAX_DELAY          = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG              = False

# Configure memory and disk queues
SCHEDULER_DISK_QUEUE            = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE          = 'scrapy.squeues.FifoMemoryQueue'

# Configure duplicate filter
DUPEFILTER_CLASS                = 'scrapy.dupefilters.RFPDupeFilter'

# Configure retry settings
RETRY_ENABLED                   = True
RETRY_TIMES                     = 3
RETRY_HTTP_CODES                = [500, 502, 503, 504, 408, 429]

# Configure timeout
DOWNLOAD_TIMEOUT                = 30

# Configure cookies
COOKIES_ENABLED                 = True

# Configure redirects
REDIRECT_ENABLED                = True
REDIRECT_MAX_TIMES              = 20

# Configure media downloads
MEDIA_ALLOW_REDIRECTS           = True

# Configure DNS timeout
DNSCACHE_ENABLED                = True
DNSCACHE_SIZE                   = 10000
DNS_TIMEOUT                     = 60


# Quality thresholds
MIN_CONTENT_LENGTH              = 10
MAX_CONTENT_LENGTH              = 100000
MIN_HEADING_LENGTH              = 1
MAX_HEADING_LENGTH              = 500
MIN_TITLE_LENGTH                = 0
MAX_TITLE_LENGTH                = 200