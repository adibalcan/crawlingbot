debug = False
log = False
save = False
elasticSearchMap = 'http://ELSTIC_SEARCH_HOST:9200/websites3'
elasticSearchEntity = elasticSearchMap + '/website3'
botName = 'CRAWLING_BOT'
userAgent = 'Mozilla/5.0 (compatible; ' + botName + '/0.3; +http://crawlingbot.com)'
maxPageSize = 1024 * 1024 # 1Mb
maxPageDownloadTime = 5 # seconds
maxWebsiteFails = 10
runFilters = True

pybloomdServer = "PYBLOOM_SERVER"

pyqServer = 'PYQ_SERVER'
pyqPort = 3334

useRedis = True
redisServer = "REDIS_SERVER"
redisPort = 6379
redisAuth = "REDIS_PASSWORD" #redis password

minPollSize = 30
threadsNumber = 10
usedMemoryMaxPercent = 45
reportInterval = 60

# inital links
seedCollection = 'website_2'
# place where we save the external links
saveExternalUrls = True
externalCollection = 'website'
requestMinIntervalForSameDomain = 1 #seconds
pagesParsedPerSite = 1

mode = 'intern'
if mode == 'intern':
    #for internal
    seedCollection = 'website'
    requestMinIntervalForSameDomain = 0 #seconds
    pagesParsedPerSite = 1
    runFilters = True
    save = True
    saveExternalUrls = False
    externalCollection = 'website'
else:
    #for external
    seedCollection = 'website_2'
    requestMinIntervalForSameDomain = 1 #seconds
    pagesParsedPerSite = 10
    runFilters = False
    save = False
    saveExternalUrls = True
    externalCollection = 'website'