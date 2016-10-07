from website import Website
from poll import Poll
import threading
from pprint import pprint
import time
import sys
import os
import config
from utils import logutils, urlutils
import gc
import codecs
sys.path.append('pyq')
from pyq import pyqclient
import json
import redis

# from pyq import pyqclient
# pyq = pyqclient.PyQClient(config.pyqServer, config.pyqPort)
from utils.queueconnection import redisQ,pyq, redisPop


poll = Poll([])

# TEST WEBSITES
websites = [
            # '{"domain":"http://info-aschaffenburg.de"}',
            # '{"domain":"http://3dhouse.ir"}',
            # '{"domain":"http://tvblast.tv"}',
            # '{"domain":"http://templatekunena.com"}',
            # '{"domain":"http://unionvgf.com"}',
            # '{"domain":"http://racheldinh.com"}',
            # '{"domain":"http://thewebminer.com"}',
            # '{"domain":"www.rakuten.co.jp"}',
            # '{"domain":"http://www.webcentric.co.rs"}',
            # '{"domain":"thewebminer.com"}',
            # '{"domain":"fakenumber.org/australia/"}',
            '{"domain":"http://pato.ro"}'
            # '{"domain":"http://thewebminer.com"}'
]

# for i in range(0,1000):
#     websites.append('{"domain":"http://thewebminer.com"}')

estimatedRequestsNumber = 0
requestLimit = 10000000
restart = False

def checkRestartCondition():
    global restart
    memory = logutils.getMemory()
    if estimatedRequestsNumber >= requestLimit:
        print('RESTART REASON: Request number is big, Memory:', memory)
        restart = True
    if memory > config.usedMemoryMaxPercent:
        restart = True
        print('RESTART REASON: Memory is over estimations Memory:', memory)
    return restart


def feeder():
    global restart, poll
    while not checkRestartCondition():
        if len(poll) < config.minPollSize:
            # print('GET A NEW BATCH OF LINKS')
            for i in range(config.minPollSize*2):
                if config.debug:
                    try:
                        website = websites.pop()
                    except:
                        website = ''
                else:
                    try:
                        if config.useRedis:
                            website = redisPop()
                        else:
                            website = pyq.pop(config.seedCollection)
                    except Exception as e:
                        logutils.log('Exception read queue', logutils.format_exception(e))
                        continue

                if website:
                    website = json.loads(website)
                    domain = website['domain']

                    if not (domain.startswith('http://') or domain.startswith('https://')):
                        domain = 'http://' + domain

                    if 'alexarank' in website:
                        poll.add(Website(domain, {"alexarank": website['alexarank']}))
                    else:
                        poll.add(Website(domain))

        # time.sleep(2)


def emergencyFeeder():
    global poll
    while len(poll) > 0:
        website = poll.pop()
        if website:
            item = {}
            domain =  urlutils.getDomain(website.startUrl)
            if "www." in domain:
                domain = domain.replace("www.","")
            item['domain'] = domain
            if 'alexarank' in website.initialMeta:
                item['alexarank'] = website.initialMeta['alexarank']
            if config.useRedis:
                # pyq.push(config.seedCollection, json.dumps(item))
                redisQ.lpush(config.seedCollection, json.dumps(item))
            else:
                pyq.push(config.seedCollection, json.dumps(item))


def doRestart(message):
    emergencyFeeder()
    print(message,flush=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)


def crawl():
    global estimatedRequestsNumber, poll
    while not restart:
        if len(poll) == 0:
            time.sleep(5)
            # print('wait for poll')
        website = poll.getWebsite()
        if website:
            try:
                website.crawlNextUrl()
                estimatedRequestsNumber += 1
                website.inProgress = False
            except Exception as e:
                website.fails += 1
                website.inProgress = False
                logutils.log('Exception', logutils.format_exception(e))
                if config.debug:
                    raise e
            if website.fails >= config.maxWebsiteFails:
                try:
                    # poll.remove(website)
                    # FORCE ENDING
                    website.ended = True
                except Exception as e:
                    logutils.log('Exception', logutils.format_exception(e))

def monitor():
    lastEstimatedRequestNumber = estimatedRequestsNumber

    while not restart:
        memory = logutils.getMemory()
        dif = estimatedRequestsNumber - lastEstimatedRequestNumber
        print(round(dif / config.reportInterval, 2), ' RPS ', round(memory, 2), '% memory ', len(poll), ' poll', flush=True)
        lastEstimatedRequestNumber = estimatedRequestsNumber
        time.sleep(config.reportInterval)


if __name__ == '__main__':
    try:
        threads = []
        # # Start Compiler
        # from utils.compiler import comp
        # print("Starting compiler")
        # comp.loadRe()
        # Start feeder
        print('start feeder', flush=True)
        feederThread = threading.Thread(target=feeder)
        feederThread.daemon = True
        feederThread.start()
        threads.append(feederThread)
        time.sleep(10)

        # monitor thread
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
        threads.append(thread)

        # Start crawling threads
        print('start crawling', flush=True)

        for i in range(config.threadsNumber):
            thread = threading.Thread(target=crawl)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        # call GC
        gc.collect()

        # The end...
        if restart:
            doRestart('EXPLICIT RESTART')
        else:
            doRestart('IMPLICIT RESTART')
    except KeyboardInterrupt:
        restart = True
        print('SAVE WEBSITES', flush=True)
        emergencyFeeder()