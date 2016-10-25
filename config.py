debug = False
log = False
save = False
elasticSearchMap = 'http://ELASTIC_SEARCH_HOST:9200/websites3'
elasticSearchEntity = elasticSearchMap + '/website3'
botName = 'CRWLING_BOT'
userAgent = 'Mozilla/5.0 (compatible; ' + botName + '/0.3; +http://example.com)'
maxPageSize = 1024 * 1024 # 1Mb
maxPageDownloadTime = 5 # seconds
maxWebsiteFails = 10
runFilters = True
useRedis = True
pyqServer = 'PYQ_HOST'
pyqPort = 3334
redisServer = "REDIS_HOST"
redisPort = 6379
redisAuth = "REDIS_PASS" #redis password
minPollSize = 30
threadsNumber = 10
usedMemoryMaxPercent = 45
reportInterval = 60
# inital links
seedCollection = 'website_2'
# place where we save the external links
saveExternalUrls = True
externalCollection = 'website'
requestMinIntervalForSameDomain = 0 #seconds
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