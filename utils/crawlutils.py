import re
import requests
from utils import urlutils, listutils

requests.packages.urllib3.disable_warnings()

linksRegex = re.compile(r'<a\s[^>]*?href=["\']{0,1}([^"\'\s>]+)', re.MULTILINE | re.IGNORECASE | re.UNICODE)
baseRegex = re.compile(r'<base\s[^>]*?href=["\']{0,1}([^"\'\s>]+)', re.MULTILINE | re.IGNORECASE | re.UNICODE)

# A special case of filter
def getLinks(source, url):
    '''return links from a page in absolute format'''
    if urlutils.isAbsolute(url):
        base = baseRegex.findall(source)
        if base:
            base = base[0]
        else:
            base = url
        links = linksRegex.findall(source)

        if links:
            # remove fragment from URL
            links = [link.split('#')[0] for link in links]
            # make absolute
            links = [urlutils.makeAbsolute(link, base, url) for link in links]
            # keep only http URLs
            links = [link for link in links if urlutils.isHttp(link)]
            # Make unique URLs and preserve URLs order
            uniqueLinks = listutils.unique(links)
            return uniqueLinks
        else:
            return []
    else:
        raise Exception('Absolute url expected')

def stripHTML (source):
    flags = flags=re.M|re.S|re.I
    source = re.sub('<script[^>]*?>[^<]*?<\/script>', '', source,flags=flags)
    source = re.sub('<style[^>]*?>[^<]*?<\/style>', '', source,flags=flags)
    source = re.sub('<!--.*?-->','',source, flags=flags)
    source = re.sub('<[^<]+?>', '', source, flags=flags)
    source = re.sub('\s+', ' ', source, flags=flags)
    return source

def detectEncodingfromHTML(source):
    oldVersion = [
        ("x-sjis","shift_jis"),
        ("gbk","UTF-8")
    ]
    match = re.search(r'<meta[^>]+charset=("|\'|)([a-zA-Z0-9-_]*)\1', source, re.IGNORECASE | re.DOTALL | re.UNICODE)
    if match and len(match.groups()) == 2:
        # print('DETECTED', match.group(2))
        encoding = match.group(2)
        for key,value in oldVersion:
            if key == encoding:
                encoding = value
        encoding = encoding.strip()
        return encoding
    else:
        return ''


