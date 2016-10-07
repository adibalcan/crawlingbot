import redis
import json
import config
redisQ = redis.StrictRedis(config.redisServer, config.redisPort, db=0)

from pyq import pyqclient
pyq = pyqclient.PyQClient(config.pyqServer, config.pyqPort)

def redisPop():
    website = ''
    data = redisQ.lpop(config.seedCollection)
    if data:
        website = str(data,"utf-8")
        # website ={'domain':website}
        # website = json.dumps(website)
    return website