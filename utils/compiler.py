
import re
import json
import os
import pprint
from utils import listutils
class Compiler:
    def __init__(self):
        self.technologies = []
        with open('filters' + os.sep + 'apps.json') as data_file:
            self.technologies = json.load(data_file)
        self.reList = {}
        self.headerList = {}
        self.impliesList = []

    def compileRe(self,key,expression,headersKey = "",implies = [],header = False):
        if implies:
            self.impliesList.append((key,implies))
        if header:
            if key in self.headerList:
                if headersKey in self.headerList[key]:
                    self.headerList[key][headersKey] = re.compile(expression,re.IGNORECASE)
                else:
                    self.headerList[key][headersKey] = []
                    self.headerList[key][headersKey] = re.compile(expression,re.IGNORECASE)
            else:
                self.headerList[key] = {}
                self.headerList[key][headersKey] = {}
                self.headerList[key][headersKey] = re.compile(expression,re.IGNORECASE)
        else:
            if key in self.reList:
                self.reList[key].append(re.compile(expression,re.IGNORECASE))
            else:
                self.reList[key]=[]
                self.reList[key].append(re.compile(expression,re.IGNORECASE))

    def implies(self,technology):
        result = []
        if 'implies' in technology:
            return True
        else:
            return False


    def loadRe(self):

        for key, technology in self.technologies['apps'].items():
            keys = ['html', 'script', 'headers']
            found = False
            for search in keys:
                if search in technology:
                    if isinstance(technology[search], list):
                        for regex in technology[search]:
                            regex = regex.split("\\;")[0]
                            if self.implies(technology):
                                result = []
                                if isinstance(technology['implies'], list):
                                    for item in technology['implies']:
                                        item = item.split("\\;")[0]
                                        result.append(item)
                                else:
                                    result.append(technology['implies'].split("\\;")[0])
                                self.compileRe(key,regex,implies = result)
                            else:
                                # COMPILE
                                self.compileRe(key,regex)
                    if search == 'headers':
                        for headersKey, headersValue in zip(technology[search].keys(), technology[search].values()):
                            headersKey = headersKey.lower()
                            if self.implies(technology):
                                result = []
                                if isinstance(technology['implies'], list):
                                    for item in technology['implies']:
                                        item = item.split("\\;")[0]
                                        result.append(item)
                                else:
                                    result.append(technology['implies'].split("\\;")[0])
                                self.compileRe(key,headersValue.split("\\;")[0],headersKey = headersKey,implies = result,header = True)
                            else:
                                # COMPILE - Done
                                self.compileRe(key,headersValue.split("\\;")[0],headersKey = headersKey,header = True)
                    if isinstance(technology[search], str):
                        # if key=="Google Analytics":
                        #     print("@!#!@#@!#!@#!@# Analytics",technology[search])
                        self.compileRe(key,technology[search].split("\\;")[0])

    def filter(self,source, meta={}):
        result = set([])
        globalFound = False
        found = False
        # print(self.reList)
        # print(self.headerList)
        # print([key for key,expression in self.reList])
        for key,expressions in self.reList.items():
            found = False
            for expression in expressions:
                if expression.search(source):
                    result.add(key)
                    found = True
                    globalFound = True
                if found:
                    for tech, implies in self.impliesList:
                        if key == tech:
                            result.add(implies)
                break
                    # break
        for key, headersKeys in self.headerList.items():
            for headersKey,headersValue in headersKeys.items():
                if headersKey in meta["headers"]:
                    if headersValue.search(meta['headers'][headersKey]):
                        result.add(key)
                        globalFound = True
        # check implies
        if globalFound:
            # make results unique and preserve order
            result = listutils.unique(result)
            return result

comp = Compiler()