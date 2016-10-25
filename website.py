import importlib as imp
import sys
import time
from collections import deque
from pprint import pprint

import requests
from utils.robotexclusionrulesparser import RobotExclusionRulesParser
from utils import logutils, urlutils, crawlutils, profileutil, listutils
sys.path.append('filters')
from utils.bloomdClient import bloom
import config
from utils import queueconnection
import json
import request

class Website:
    def __init__(self, startUrl, initialMeta = {}):
        self.startUrl = startUrl
        self.parsedUrls = []
        self.externalLinks = []
        self.domain = urlutils.getDomain(startUrl)
        self.parsedPages = 0
        self.lastRequest = time.time()
        self.requestMinInterval = 1 #not used
        self.parseLimit = config.pagesParsedPerSite
        self.fails = 0
        self.inProgress = False
        self.repr = RobotExclusionRulesParser()
        self.initialMeta = initialMeta #contains metainfo for filters
        self.updateMode = True
        # self.client = BloomdClient(["107.170.243.148"])
        # self.bloom = self.client.create_filter("domains")
        try:
            # TODO: get protocol for startURL
            response = crawlutils.getSource('http://' + self.domain + '/robots.txt')
            robotsTxt = response.text

            # get last url in a sequence of redirects
            if response.reason == 'OK':
                self.startUrl = response.url
        except:
            robotsTxt = ''
        self.repr.parse(robotsTxt)
        self.firstPageFiltersData = {}

        # check starturl against robots.txt
        if not self.repr.is_allowed(config.botName, startUrl):
            # utils.log('crawling root forbiden by robots.txt')
            self.ended = True
        else:
            self.ended = False

        self.filters = [
                            {'name': 'textratio'},
                            {'name': 'title'},
                            {'name': 'keywords'},
                            {'name': 'description'},
                            {'name': 'numberofimages'},
                            {'name': 'numberoflinks'}
                        ]
        # Load filters

        for filter in self.filters:
            filter['mod'] = imp.import_module(filter['name'])

        self.firstPageFilters =  [
                                  {'name': 'encoding'},
                                  {'name': 'tech'},
                                  # {'name': 'technew'},
                                  {'name': 'isresponsive'},
                                  {'name': 'isblog'},
                                  {'name': 'topleveldomain'},
                                  {'name': 'linkedin'},
                                  {'name': 'haslinkedin'},
                                  {'name': 'facebook'},
                                  {'name': 'hasfacebook'},
                                  {'name': 'twitter'},
                                  {'name': 'hastwitter'},
                                  {'name': 'language'},
                                  {'name': 'femail'},
                                  {'name': 'hasemail'},
                                  {'name': 'phone'},
                                  {'name': 'hasphone'},
                                  {'name': 'iscompany'},
                                  {'name': 'alexarank'}
                                 ]
        for filter in self.firstPageFilters:
            filter['mod'] = imp.import_module(filter['name'])

        # TODO: this need to be unique
        # TODO: put a bloomfiltere here
        self.toParse = deque([startUrl])

    def crawlNextUrl(self):
        if self.ended:
            return False

        if len(self.toParse) > 0:
            currentUrl = self.toParse.popleft()
        else:
            self.save()
            self.ended = True
            if config.log:
                logutils.log('end: empty internal links queue', self.toParse)
            return False

        if config.log:
            print(currentUrl)

        self.lastRequest = time.time()

        response = request.getSource(currentUrl)

        if not self.isValidResponse(response):
            # utils.log('invalid response', currentUrl)
            return False

        source = response.textcontent

        # GET NEW LINKS
        newLinks = crawlutils.getLinks(source, currentUrl)
        # remove external links
        internalNewLinks = [link for link in newLinks if urlutils.isInternalLink(link, currentUrl)]
        # remove current url
        internalNewLinks = [link for link in internalNewLinks if link != currentUrl]
        # remove invalid extensions
        internalNewLinks = [link for link in internalNewLinks if urlutils.validExtension(link)]
        # remove already parsed URLs
        internalNewLinks = [link for link in internalNewLinks if link not in [l['url'] for l in self.parsedUrls]]
        # remove already enqueued URLs
        internalNewLinks = [link for link in internalNewLinks if link not in self.toParse]
        # remove URLs restricted by robots.txt
        internalNewLinks = [link for link in internalNewLinks if self.repr.is_allowed(config.botName, link)]
        # if config.debug: utils.log('links', internalNewLinks)
        self.toParse.extend(internalNewLinks)

        # EXTERNAL LINKS
        # remove internal links
        externalNewLinks = internalNewLinks = [link for link in newLinks if not urlutils.isInternalLink(link, currentUrl)]
        # remove already enqueued URLs
        externalNewLinks = [link for link in externalNewLinks if link not in self.externalLinks]
        self.externalLinks.extend(externalNewLinks)

        self.parsedPages += 1

        meta = {"url": response.url, "response": response, "headers": response.headers, 'newLinks': newLinks, 'internalNewLinks': internalNewLinks, 'domain':self.domain}
        meta.update(self.initialMeta)

        # RUN FIRST PAGE FILTERS
        if self.parsedPages == 1:
            result = self.runFilters(source, meta, self.firstPageFilters)
            self.firstPageFiltersData = result

        # RUN PAGE FILTERS
        result = self.runFilters(source, meta, self.filters)
        self.parsedUrls.append(result)

        if self.parsedPages >= self.parseLimit:
            self.save()
            self.ended = True
            if config.log:
                logutils.log('end: hit parse limit')
            return False
        return True

    def isValidResponse(self, response):
        # some response filters
        if not response.status_code:
            return False
        else:
             if response.status_code < 200 or response.status_code > 299:
                 return False

        # avoid non text/html resources
        if 'content-type' in response.headers:
            if 'text' not in response.headers['content-type']:
                return False
        return True

    def runFilters(self, source, meta, filters):
        result = {}
        if config.runFilters:
            for filter in filters:
                meta.update(result)
                start = time.clock()
                result['filter_'+filter['name']] = filter['mod'].filter(source, meta)
                profileutil.profile.save(filter['name'], time.clock() - start)

        result['url'] = meta['url']
        return result

    def save(self):
        keys = ['startUrl', 'firstPageFiltersData', 'toParse', 'parsedUrls', 'domain', 'parsedPages', 'lastRequest']
        result = {}
        for key in keys:
            item = getattr(self, key)
            if isinstance(item, deque):
                item = list(item)
            result[key] = item

        # Transofrm list in object...
        # We need this strnge format for partial update in ElasticSearch
        data = {}
        i=0
        for item in result['parsedUrls']:
            data[str(i)] = item
            i+=1
        result['parsedUrls'] = data

        if config.debug:
            pprint(result)
            # profileutil.profile.show()

        # Save / update in ES
        if config.save and len(result['parsedUrls']) > 0:
            if self.updateMode:
                updateData = {}
                updateData['doc'] = result
                updateData['doc_as_upsert'] = True
                r = requests.post(config.elasticSearchEntity + '/' + result['domain'] + '/_update', data=json.dumps(updateData))
            else:
                r = requests.put(config.elasticSearchEntity + '/' + result['domain'], data=json.dumps(result))
            bloom.add(result['domain'])
            if config.debug: print(r.content)
        self.saveExternalUrls()

    def saveExternalUrls(self):
        if config.saveExternalUrls:
            externalDomains = [urlutils.getDomain(domain) for domain in self.externalLinks]
            print(externalDomains)
            externalDomains = [domain for domain in externalDomains if domain]
            # remove www.
            externalDomains = [domain if not domain.startswith('www.') else domain[4:] for domain in externalDomains]
            externalDomains = listutils.unique(externalDomains)

            for domain in externalDomains:
                schemaLessDomain = urlutils.removeSchema(domain)
                if bloom.add(domain):
                    item = {}
                    item['domain'] = schemaLessDomain
                    # pprint(item)
                    queueconnection.push(config.externalCollection, json.dumps(item))

    def update(self):
        pass