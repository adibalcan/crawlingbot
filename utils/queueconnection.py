import redis
import json
import config
redisQ = redis.StrictRedis(config.redisServer, config.redisPort, db=0, password = config.redisAuth)

from pyq import pyqclient
pyq = pyqclient.PyQClient(config.pyqServer, config.pyqPort)

def pop(collection):
    if config.useRedis:
        # REDIS
        website = ''
        data = redisQ.lpop(collection)
        if data:
            website = str(data,"utf-8")
            # website ={'domain':website}
            # website = json.dumps(website)
        return website
    else:
        # PYQ
        website = pyq.pop(collection)
        return website

def push(collection, data):
    if config.useRedis:
        redisQ.lpush(collection, data)
    else:
        pyq.push(collection, data, withIndex = True)


